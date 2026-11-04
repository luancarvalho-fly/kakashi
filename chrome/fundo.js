// Kakashi — olho no Chrome (04/11/2026). O fundo da extensão: recebe o elemento que o olho.js achou debaixo do mouse e manda pro
// Kakashi (127.0.0.1:7816, POST /chrome). Só manda enquanto o Kakashi está gravando (GET /status, guardado por 2 s); Kakashi fechado
// ou parado = nada sai do Chrome. Nada vai pra fora do PC.
const KAKASHI = "http://127.0.0.1:7816";
let estado = {t: 0, gravando: false};

async function gravando() {
  if (Date.now() - estado.t < 2000) return estado.gravando;
  estado.t = Date.now();
  try {
    const r = await fetch(KAKASHI + "/status", {cache: "no-store"});
    const s = await r.json();
    estado.gravando = s.estado === "gravando" && !s.pausado;
  } catch (e) {
    estado.gravando = false;           // Kakashi fechado
  }
  return estado.gravando;
}

chrome.runtime.onMessage.addListener((msg, quem, responder) => {
  if (msg && msg.tipo === "gravando?") {
    gravando().then(g => responder({gravando: g}));
    return true;
  }
  if (msg && msg.tipo === "elemento") {
    gravando().then(g => {
      if (!g) return;
      const d = Object.assign({}, msg.dados, {aba: quem.tab ? quem.tab.id : null, frame: quem.frameId || 0});
      fetch(KAKASHI + "/chrome", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(d)})
        .catch(() => { estado.t = 0; });
    });
  }
});
