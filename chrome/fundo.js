// Kakashi — olho no Chrome (04/11/2026). O fundo da extensão: recebe o elemento que o olho.js achou debaixo do mouse e manda pro
// Kakashi (127.0.0.1:7816, POST /chrome). Só manda enquanto o Kakashi está gravando (GET /status, guardado por 2 s); Kakashi fechado
// ou parado = nada sai do Chrome. Nada vai pra fora do PC.
//
// SE RECARREGA SOZINHA (04/11, ele: «Pode fazer», sobre o buraco do ATUALIZAR): o ATUALIZAR do Kakashi troca os arquivos desta pasta,
// mas o Chrome segue rodando o código velho. Na hora em que esta versão entra (instalada, recarregada ou Chrome aberto), guardo a
// impressão (SHA-256) dos arquivos como estão no disco; a cada minuto comparo de novo: mudou = chrome.runtime.reload(). Ao entrar,
// ponho o olho também nas guias que já estavam abertas (sem precisar de F5). A impressão fica no chrome.storage.local («carregada»).
const KAKASHI = "http://127.0.0.1:7816";
const ARQUIVOS = ["manifest.json", "fundo.js", "olho.js", "fonte.js"];
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
  if (estado.gravando) vigiarTracos();
  return estado.gravando;
}

// ---------- KAKASHI 3.0 (12/11/2026): o elemento do Chrome debaixo da PONTA DO DESENHO ----------
// Desenhando, o mouse está na janela do desenho do Kakashi, não no Chrome: o olho.js não vê nada. O Kakashi põe no /status o
// «pedido_chrome» {id, x, y, escala} (a ponta do traço, em pixel da tela) e eu peço à guia da frente da janela do Chrome que está
// ali o elemento nesse ponto (o mesmo descrever() do olho.js, com o código-fonte). Só enquanto o Kakashi grava.
let vigiando = false, ultPedido = 0;
async function vigiarTracos() {
  if (vigiando) return;
  vigiando = true;
  try {
    for (;;) {
      let s;
      try { s = await (await fetch(KAKASHI + "/status", {cache: "no-store"})).json(); } catch (e) { break; }
      if (s.estado !== "gravando") break;
      const p = s.pedido_chrome;
      if (p && p.id !== ultPedido) { ultPedido = p.id; await descreverPonto(p).catch(() => {}); }
      chrome.runtime.getPlatformInfo(() => {});            // chamada de extensão = o fundo não dorme enquanto grava
      await new Promise(ok => setTimeout(ok, s.ferramenta && s.ferramenta !== "cursor" ? 300 : 1500));
    }
  } finally {
    vigiando = false;
  }
}

async function descreverPonto(p) {
  const esc = p.escala || 1, x = p.x / esc, y = p.y / esc;          // pixel da tela → DIP (o que o Chrome usa nas janelas)
  const janelas = await chrome.windows.getAll({populate: true, windowTypes: ["normal", "popup", "app"]});
  const dentro = janelas.filter(w => w.state !== "minimized" && x >= w.left && x < w.left + w.width && y >= w.top && y < w.top + w.height);
  const w = dentro.find(j => j.focused) || dentro[0];
  const aba = w && w.tabs.find(t => t.active);
  if (!aba || !/^(https?|file):/.test(aba.url || "")) return;
  const r = await chrome.tabs.sendMessage(aba.id, {tipo: "descrever-ponto", x, y, escala: esc}, {frameId: 0}).catch(() => null);
  if (!r || !r.dados) return;
  const d = Object.assign({}, r.dados, {aba: aba.id, frame: 0, pedido: p.id});
  await fetch(KAKASHI + "/chrome", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(d)}).catch(() => {});
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

// ---------- se recarregar sozinha ----------
async function impressao() {
  let tudo = "";
  for (const a of ARQUIVOS) {
    const r = await fetch(chrome.runtime.getURL(a), {cache: "no-store"});
    tudo += a + "\n" + (await r.text()) + "\n";
  }
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(tudo));
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, "0")).join("");
}

async function conferir() {
  try {
    const {carregada} = await chrome.storage.local.get("carregada");
    const agora = await impressao();
    if (!carregada) { await chrome.storage.local.set({carregada: agora}); return "guardada"; }
    if (agora !== carregada) { chrome.runtime.reload(); return "recarregando"; }
    return "igual";
  } catch (e) {
    return "erro: " + e;                 // arquivo no meio da cópia: confere de novo no próximo minuto
  }
}

async function entrarNasGuias() {
  const abas = await chrome.tabs.query({});
  for (const a of abas) {
    if (!a.id || !/^(https?|file):/.test(a.url || "")) continue;
    try {
      await chrome.scripting.executeScript({target: {tabId: a.id, allFrames: true}, files: ["fonte.js"], world: "MAIN"});
      await chrome.scripting.executeScript({target: {tabId: a.id, allFrames: true}, files: ["olho.js"]});
    } catch (e) { /* guia que o Chrome não deixa (loja, página de erro) */ }
  }
}

async function entrou() {
  await chrome.storage.local.set({carregada: await impressao()});
  await entrarNasGuias();
}

chrome.runtime.onInstalled.addListener(() => { entrou(); });      // instalada ou recarregada (inclusive pelo reload acima)
chrome.runtime.onStartup.addListener(() => { entrou(); });        // Chrome aberto: o código que roda é o do disco agora
chrome.alarms.create("conferir", {periodInMinutes: 1});
chrome.alarms.onAlarm.addListener(a => { if (a.name === "conferir") { conferir(); gravando(); } });   // 3.0: acorda o vigia do desenho


