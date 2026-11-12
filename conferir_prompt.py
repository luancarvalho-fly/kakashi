# -*- coding: utf-8 -*-
"""O CONFERIDOR do modo RÁPIDO do Kakashi (3.0, 12/11/2026) — o sabotador barato, por script, sem agente.

Pedido dele (chat 12/11): «você acha que vale a pena ter um sabotador?... o sabotador seria melhor só pra correção pesada mesmo,
gravação muito longa?... às vezes eu sinto que o Kakashi demora muito pra resolver coisas bobas» + sobre o PROMPT do rápido:
«prompt curto abre muita margem de erro pra você não fazer o que eu te pedi... o prompt tem que ser o necessário, nem pra menos, nem
pra mais».

O que ele confere: TODA fala com conteúdo da gravação tem dono no PROMPT.md — um [mm:ss] citado perto dela (tarefa, «Não fazer
agora», «Dúvidas», «Pergunta dele») ou um trecho [m:ss–m:ss] na seção «Fora» (conversa solta, repetição, pensando alto). Fala sem
dono = pedido que pode ter sumido na reescrita: é exatamente o «passou batido» que o sabotador pegava.

  python conferir_prompt.py <pasta> [<outra pasta> ...] [--prompt <PROMPT.md>]

Várias pastas = gravações seguidas juntadas num PROMPT só: aí a citação pode levar a hora da gravação na frente, [1715 1:23]; sem
a hora, vale pra todas. Escreve COBERTURA.md do lado do PROMPT.md («RESULTADO: OK» ou «RESULTADO: FALTA n») e sai 0 (ok) ou 1.
A trava (kakashi_lidas.py marcar) do modo RÁPIDO só aceita COBERTURA OK mais nova que o PROMPT.md.
"""
import datetime, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from resumo_pc import palavras, mmss  # noqa: E402   (as palavras que contam: 4+ letras, fora as de encher linguiça)

FOLGA = 6.0          # segundos: a citação [mm:ss] vale pra fala que começa até 6 s depois ou termina até 6 s antes
CITA = re.compile(r"\[(?:(\d{4})\s+)?(\d{1,3}):(\d{2})(?:\s*[–—-]\s*(\d{1,3}):(\d{2}))?\]")


def falas(pasta):
    """[(ini, fim, texto)] no relógio da gravação — PC, Premiere (painel ou o olho) ou o app de cartões"""
    fontes = [("fala_transcricao.json", lambda d: [(a, b, t) for a, b, t in d["segmentos"]]),
              (os.path.join("_transcricao", "fala.tandera.json"), lambda d: [(s["ini"], s["fim"], s["txt"]) for s in d["segmentos"]]),
              (os.path.join("_olho", "fala_transcricao.json"), lambda d: [(a, b, t) for a, b, t in d["segmentos"]]),
              ("fala.A.json", lambda d: [(s["start"], s["end"], s.get("text") or "") for s in d])]
    for nome, ler in fontes:
        arq = os.path.join(pasta, nome)
        if os.path.isfile(arq):
            try:
                return ler(json.load(open(arq, encoding="utf-8"))), nome
            except (ValueError, KeyError, TypeError) as e:
                print("aviso: %s não leu (%s)" % (arq, e))
    return None, None


def hora(pasta):
    """a hora da gravação no nome da pasta (2026-11-12_151530_pc → 1515; 2026-11-04_1651_V015 → 1651)"""
    m = re.match(r"\d{4}-\d{2}-\d{2}_(\d{4})", os.path.basename(pasta.rstrip("\\/")))
    return m.group(1) if m else None


def achar_prompt(pastas, dado):
    if dado:
        return dado
    for p in pastas:
        for c in (os.path.join(p, "PROMPT.md"), os.path.join(p, "_transcricao", "PROMPT.md")):
            if os.path.isfile(c):
                return c
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    dado = None
    if "--prompt" in a:
        i = a.index("--prompt"); dado = a[i + 1]; del a[i:i + 2]
    pastas = [os.path.abspath(p) for p in a if not p.startswith("--")]
    if not pastas:
        sys.exit(__doc__)
    prompt = achar_prompt(pastas, dado)
    if not prompt:
        sys.exit("sem PROMPT.md na pasta (nem em _transcricao\\): escrever o PROMPT antes de conferir")
    texto = open(prompt, encoding="utf-8").read()
    citas = []                                   # (hora ou None, ini, fim)
    for m in CITA.finditer(texto):
        h, a1, b1, a2, b2 = m.groups()
        ini = int(a1) * 60 + int(b1)
        fim = int(a2) * 60 + int(b2) if a2 else None
        citas.append((h, ini, fim))
    sem_dono, total, cobertas, fora_da_gravacao = [], 0, 0, []
    for p in pastas:
        segs, fonte = falas(p)
        if segs is None:
            sys.exit("sem transcrição em %s: rodar o resumo (resumo_pc.py / a transcrição do Premiere) antes" % p)
        h = hora(p)
        minhas = [(i, f) for hh, i, f in citas if hh is None or hh == h]
        dur = max([b for _, b, _ in segs] or [0])
        fora_da_gravacao += ["[%s%s]" % ((hh + " ") if hh else "", mmss(i)) for hh, i, f in citas
                             if (hh is None or hh == h) and len(pastas) == 1 and i > dur + 30]
        for ini, fim, tx in segs:
            if len(palavras(tx)) < 2 or tx.strip().startswith("[whisper"):
                continue                         # «ó», «tá», «beleza»: sem conteúdo pra ter dono
            total += 1
            dono = any((f is None and ini - FOLGA <= i <= fim + FOLGA) or (f is not None and i - 1 <= fim and f + 1 >= ini)
                       for i, f in minhas)
            if dono:
                cobertas += 1
            else:
                sem_dono.append((h if len(pastas) > 1 else None, ini, tx.strip()))
    ok = not sem_dono
    linhas = ["# COBERTURA do PROMPT · %s" % datetime.datetime.now().strftime("%d/%m %H:%M"),
              "RESULTADO: %s" % ("OK" if ok else "FALTA %d" % len(sem_dono)), "",
              "prompt: `%s` · gravações: %s" % (prompt, ", ".join(os.path.basename(p) for p in pastas)),
              "falas com conteúdo: %d · com dono no PROMPT: %d · citações [mm:ss] no PROMPT: %d" % (total, cobertas, len(citas)), ""]
    if sem_dono:
        linhas += ["## Falas SEM DONO — cada uma vira tarefa, «Não fazer agora», «Dúvidas» ou entra na seção «Fora» (com o [mm:ss]);",
                   "## depois rodar de novo. Não é pra inventar tarefa: fala que não pede nada vai pro «Fora».", ""]
        linhas += ["- [%s%s] «%s»" % ((h + " ") if h else "", mmss(i), tx[:300]) for h, i, tx in sem_dono]
        linhas.append("")
    if fora_da_gravacao:
        linhas += ["## Aviso: citação depois do fim da gravação (minuto errado?): " + ", ".join(fora_da_gravacao), ""]
    saida = os.path.join(os.path.dirname(prompt), "COBERTURA.md")
    open(saida, "w", encoding="utf-8").write("\n".join(linhas))
    print("\n".join(linhas[:5]))
    print(saida)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
