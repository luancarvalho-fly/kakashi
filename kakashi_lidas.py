# -*- coding: utf-8 -*-
"""REGISTRO DOS KAKASHI JÁ LIDOS — vale pra TODOS os chats (pedido dele 24/10 15h40: "você tem que colocar um registro dos Kakashi que já
foram lidos... Esse do Spotify eu já usei em outro chat, não era pra você ter lido ele").
Cada correção lida ganha um LIDA.json DENTRO da própria pasta da sessão (quem leu, quando, em que chat, o que virou). Um chat novo NUNCA
lê uma sessão marcada. Também conta como lida (outro chat já trabalhou nela, mesmo sem a marca): LEITURA-CLAUDE.md na pasta ou em
_transcricao\\, ou o nome da pasta no lidas.json da skill /kakashi.

  python kakashi_lidas.py novas                  → as correções AINDA NÃO LIDAS (PC, Premiere e AppPessoal), da mais nova pra mais velha
  python kakashi_lidas.py marcar <pasta> --chat <id do chat> [--nota "o que virou"]   → marca como lida (LIDA.json + lidas.json)
  python kakashi_lidas.py quem <pasta>           → quem leu essa sessão
  python kakashi_lidas.py faltando               → sessões de hoje sem LEITURA-CLAUDE.md ou SABOTADOR.md (a análise que faltou)
TRAVA 06/11: marcar com nota final só passa com LEITURA-CLAUDE.md + SABOTADOR.md na pasta; «--nota lendo» reserva sem exigir.
"""
import datetime, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))   # pacote da Fly: tudo relativo à pasta do Kakashi

BASES = [("PC", os.path.join(AQUI, "sessoes")), ("Premiere", os.path.join(AQUI, "premiere", "sessoes"))]
LIDAS = os.path.join(AQUI, "lidas.json")


def lidas_skill():
    try:
        return json.dumps(json.load(open(LIDAS, encoding="utf-8")), ensure_ascii=False)
    except Exception:
        return ""


def info(p):
    s = {}
    try:
        s = json.load(open(os.path.join(p, "sessao.json"), encoding="utf-8"))
    except Exception:
        pass
    return s


def ja_lida(p, texto_lidas):
    nome = os.path.basename(p.rstrip("\\/"))
    if os.path.isfile(os.path.join(p, "LIDA.json")):
        try:
            return "LIDA.json: " + json.load(open(os.path.join(p, "LIDA.json"), encoding="utf-8")).get("chat", "?")
        except Exception:
            return "LIDA.json"
    for c in (os.path.join(p, "LEITURA-CLAUDE.md"), os.path.join(p, "_transcricao", "LEITURA-CLAUDE.md")):
        if os.path.isfile(c):
            return "outro chat já leu (LEITURA-CLAUDE.md)"
    if nome and nome in texto_lidas:
        return "lidas.json da skill"
    return ""


def novas():
    t = lidas_skill(); out = []
    for tipo, base in BASES:
        if not os.path.isdir(base):
            continue
        for n in os.listdir(base):
            p = os.path.join(base, n)
            if not os.path.isdir(p) or n.startswith("_"):
                continue
            s = info(p)
            if s.get("descartada"):
                continue
            if ja_lida(p, t):
                continue
            out.append((os.path.getmtime(p), tipo, p, s.get("duracao_s") or s.get("partes", [{}])[0].get("dur") if s.get("partes") else s.get("duracao_s"),
                        s.get("continua_em")))
    out.sort(reverse=True)
    if not out:
        print("nenhuma correção nova (todas já lidas)")
    for m, tipo, p, dur, cont in out:
        print("%s · %-8s · %s · %s%s" % (datetime.datetime.fromtimestamp(m).strftime("%d/%m %H:%M"), tipo, os.path.basename(p),
                                        ("%.0f s" % dur) if isinstance(dur, (int, float)) else "?", (" · CONTINUA NO " + cont.upper()) if cont else ""))


def tem(p, nome):
    return any(os.path.isfile(c) for c in (os.path.join(p, nome), os.path.join(p, "_transcricao", nome)))


def marcar(p, chat, nota):
    # TRAVA (06/11, ele: «você tá lendo as correções do Kakashi sem analisar elas antes... por isso que tá passando coisa batida...
    # Você não pode fazer isso»): nas 11 correções de 06/11 eu fui da transcrição direto pro código. Agora só dá pra marcar como LIDA
    # (nota final) com a LEITURA-CLAUDE.md (passo 4 da skill) e a SABOTADOR.md (passo 4c: o que o sabotador achou e o que eu corrigi)
    # na pasta. «lendo» (reservar a sessão pra outro chat não pegar) continua livre.
    if nota.strip().lower() != "lendo":
        falta = [n for n in ("LEITURA-CLAUDE.md", "SABOTADOR.md") if not tem(p, n)]
        if falta:
            print("NÃO MARCADA: falta " + " e ".join(falta) + " em " + p)
            print("  Passo 4: escrever a LEITURA-CLAUDE.md (pedidos com fala literal [mm:ss], erros meus, o que fica, dúvidas).")
            print("  Passo 4c: rodar o sabotador (agente separado) e gravar SABOTADOR.md com os achados e o que mudou na leitura.")
            sys.exit(1)
    d = {"lida_em": datetime.datetime.now().replace(microsecond=0).isoformat(), "chat": chat, "nota": nota}
    json.dump(d, open(os.path.join(p, "LIDA.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    try:
        L = json.load(open(LIDAS, encoding="utf-8"))
        item = "%s (%s; chat %s): %s" % (os.path.basename(p), d["lida_em"], chat[:8], nota)
        if isinstance(L, list):
            L.append(item)
        elif isinstance(L, dict):
            alvo = next((k for k in ("lidas", "sessoes") if isinstance(L.get(k), list)), None)
            if alvo:
                L[alvo].append(item)
            else:
                L[os.path.basename(p)] = item
        json.dump(L, open(LIDAS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception as e:
        print("lidas.json não atualizado:", e)
    print("marcada:", p)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a or a[0] == "novas":
        novas()
    elif a[0] == "marcar":
        chat = a[a.index("--chat") + 1] if "--chat" in a else "?"
        nota = a[a.index("--nota") + 1] if "--nota" in a else ""
        marcar(a[1], chat, nota)
    elif a[0] == "faltando":
        hoje = datetime.date.today().isoformat()
        for tipo, base in BASES:
            if not os.path.isdir(base):
                continue
            for n in sorted(os.listdir(base)):
                p = os.path.join(base, n)
                if os.path.isdir(p) and n.startswith(hoje) and not n.startswith("_"):
                    f = [x for x in ("LEITURA-CLAUDE.md", "SABOTADOR.md") if not tem(p, x)]
                    if f:
                        print("%-8s %s · falta %s" % (tipo, n, ", ".join(f)))
    elif a[0] == "quem":
        print(ja_lida(a[1], lidas_skill()) or "ninguém leu ainda")


if __name__ == "__main__":
    main()
