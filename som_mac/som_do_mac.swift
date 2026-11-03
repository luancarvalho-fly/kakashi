// SOM DO MAC (porte do Kakashi pro Mac, 02/11/2026): o que sai no som do Mac, pelo ScreenCaptureKit (macOS 13+), sem driver.
// No Windows quem faz isto é o WASAPI loopback do gravar_pc.py; no Mac o gravar_pc.py chama este programa e lê o som dele.
//
//   som_do_mac            → PCM 16 bits, 48 kHz, estéreo, intercalado, no stdout (até ser fechado ou morto)
//   som_do_mac --conferir → só confere se o Mac deixa capturar (sai 0 = deixa)
//
// stderr: uma linha por acontecimento ("ok ...", "erro ..."). Só escuta: não toca som nem grava a tela (a imagem pedida é
// de 2x2 pixels, 1 por segundo, e é jogada fora). Precisa da permissão Gravação de Tela e Áudio do Sistema.
import Foundation
import ScreenCaptureKit
import CoreMedia
import AudioToolbox

let TAXA = 48000
let CANAIS = 2

func avisar(_ s: String) {
    FileHandle.standardError.write((s + "\n").data(using: .utf8)!)
}

final class Ouvido: NSObject, SCStreamOutput, SCStreamDelegate {
    let saida = FileHandle.standardOutput
    var avisouFormato = false

    func stream(_ stream: SCStream, didOutputSampleBuffer sb: CMSampleBuffer, of tipo: SCStreamOutputType) {
        guard tipo == .audio, sb.isValid,
              let fd = sb.formatDescription,
              let asbdP = CMAudioFormatDescriptionGetStreamBasicDescription(fd) else { return }
        let asbd = asbdP.pointee
        let n = CMSampleBufferGetNumSamples(sb)
        let ch = max(1, Int(asbd.mChannelsPerFrame))
        let flutuante = asbd.mFormatFlags & kAudioFormatFlagIsFloat != 0
        let separado = asbd.mFormatFlags & kAudioFormatFlagIsNonInterleaved != 0
        if !avisouFormato {
            avisouFormato = true
            avisar("ok formato \(Int(asbd.mSampleRate)) Hz, \(ch) canal(is), \(flutuante ? "float" : "int")\(separado ? " separado" : "")")
        }
        var out = [Int16](repeating: 0, count: n * CANAIS)
        do {
            try sb.withAudioBufferList { abl, _ in
                for c in 0..<CANAIS {
                    let cc = min(c, ch - 1)
                    let buf = separado ? abl[cc] : abl[0]
                    guard let dados = buf.mData else { continue }
                    let passo = separado ? 1 : ch
                    let ini = separado ? 0 : cc
                    if flutuante {
                        let p = dados.assumingMemoryBound(to: Float.self)
                        for i in 0..<n {
                            let v = max(-1.0, min(1.0, p[i * passo + ini]))
                            out[i * CANAIS + c] = Int16(v * 32767.0)
                        }
                    } else {
                        let p = dados.assumingMemoryBound(to: Int16.self)
                        for i in 0..<n { out[i * CANAIS + c] = p[i * passo + ini] }
                    }
                }
            }
        } catch {
            return
        }
        out.withUnsafeBytes { saida.write(Data($0)) }
    }

    func stream(_ stream: SCStream, didStopWithError erro: Error) {
        avisar("erro a captura parou: \(erro.localizedDescription)")
        exit(2)
    }
}

signal(SIGPIPE, SIG_IGN)
let conferir = CommandLine.arguments.contains("--conferir")
let ouvido = Ouvido()
var fluxo: SCStream?

Task {
    do {
        let conteudo = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
        guard let tela = conteudo.displays.first else {
            avisar("erro nenhuma tela encontrada"); exit(3)
        }
        if conferir {
            avisar("ok o Mac deixa capturar o som"); exit(0)
        }
        let filtro = SCContentFilter(display: tela, excludingWindows: [])
        let cfg = SCStreamConfiguration()
        cfg.capturesAudio = true
        cfg.excludesCurrentProcessAudio = true
        cfg.sampleRate = TAXA
        cfg.channelCount = CANAIS
        cfg.width = 2
        cfg.height = 2
        cfg.minimumFrameInterval = CMTime(value: 1, timescale: 1)
        let s = SCStream(filter: filtro, configuration: cfg, delegate: ouvido)
        try s.addStreamOutput(ouvido, type: .audio, sampleHandlerQueue: DispatchQueue(label: "som"))
        try s.addStreamOutput(ouvido, type: .screen, sampleHandlerQueue: DispatchQueue(label: "tela"))
        try await s.startCapture()
        fluxo = s
        avisar("ok gravando o som do Mac (\(TAXA) Hz, \(CANAIS) canais)")
    } catch {
        avisar("erro \(error.localizedDescription)")
        exit(4)
    }
}
RunLoop.main.run()
