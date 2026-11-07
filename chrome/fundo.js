// Kakashi — olho no Chrome (04/11/2026). O fundo da extensão: recebe o elemento que o olho.js achou debaixo do mouse e manda pro
// Kakashi (127.0.0.1:7816, POST /chrome). Só manda enquanto o Kakashi está gravando (GET /status, guardado por 2 s); Kakashi fechado
// ou parado = nada sai do Chrome. Nada vai pra fora do PC.
//
// SE RECARREGA SOZINHA (04/11, ele: «Pode fazer», sobre o buraco do ATUALIZAR): o ATUALIZAR do Kakashi troca os arquivos desta pasta,
// mas o Chrome segue rodando o código velho. Na hora em que esta versão entra (instalada, recarregada ou Chrome aberto), guardo a
// impressão (SHA-256) dos arquivos como estão no disco; a cada minuto comparo de novo: mudou = chrome.runtime.reload(). Ao entrar,
// ponho o olho também nas guias que já estavam abertas (sem precisar de F5). A impressão fica no chrome.storage.local («carregada»).
const KAKASHI = "http://127.0.0.1:7816";
const ARQUIVOS = ["manifest.json", "fundo.js", "olho.js", "fonte.js", "ponte.js"];
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

// páginas do Fly X-tudo (as mesmas do manifest): depois de um reload a ponte.js velha morre junto com o contexto; ponho a nova
// na hora, sem F5 (Kakashi 07/11 00:42: «tem que ser automático, eu entrar no Fly Studio e acabou e usar»)
const PONTE_EM = /^(https:\/\/flyxtudo-fly-media\.vercel\.app|http:\/\/127\.0\.0\.1:3007|http:\/\/localhost:3007)\//;
async function entrarNasGuias() {
  const abas = await chrome.tabs.query({});
  for (const a of abas) {
    if (!a.id || !/^(https?|file):/.test(a.url || "")) continue;
    try {
      await chrome.scripting.executeScript({target: {tabId: a.id, allFrames: true}, files: ["fonte.js"], world: "MAIN"});
      await chrome.scripting.executeScript({target: {tabId: a.id, allFrames: true}, files: ["olho.js"]});
      if (PONTE_EM.test(a.url)) await chrome.scripting.executeScript({target: {tabId: a.id, allFrames: true}, files: ["ponte.js"]});
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
chrome.alarms.onAlarm.addListener(a => { if (a.name === "conferir") conferir(); });


// ---------- ponte Fly X-tudo → Fly Studio (06/11/2026) ----------
// O Fly X-tudo pede (pela ponte.js) e eu falo com a API do Fly Studio com o login deste Chrome: a geração sai do crédito do Fly e fica
// no Cinema. Trava: só páginas do Fly X-tudo, só o IP Plexus, só ler produção/gerações/modelos, criar cena/shot e pedir geração no
// canvas, subir imagem de referência pra biblioteca do Fly e baixar a saída de uma geração. Mais nada.
const FLY_API = "https://api.studio.flymedia.ai";
const FLY_IP = "019d4eef-daea-7289-851b-b6d628926d99";
const ORIGENS_FX = ["https://flyxtudo-fly-media.vercel.app", "http://127.0.0.1:3007", "http://localhost:3007"];
const U = "[0-9a-f-]{36}";
const ROTAS = [
  ["GET", new RegExp(`^/v1/auth/session/verify$`)],
  ["GET", new RegExp(`^/v1/models$`)],
  ["GET", new RegExp(`^/v1/workspaces/019d4ee4-642d-742d-84d9-28e0558f18ec/ips/${FLY_IP}/spending-limits$`)],
  ["GET", new RegExp(`^/v1/ips/${FLY_IP}/productions/${U}$`)],
  ["GET", new RegExp(`^/v1/ips/${FLY_IP}/canvas/${U}/predictions$`)],
  ["POST", new RegExp(`^/v1/ips/${FLY_IP}/productions/${U}/(scenes|shots)$`)],
  ["POST", new RegExp(`^/v1/ips/${FLY_IP}/canvas/${U}/predictions/(videos|images)$`)],
  ["POST", new RegExp(`^/v1/ips/${FLY_IP}/media-cookies$`)],
];
/* 07/11/2026 (Kakashi 00:11: «Não consegui achar/criar o shot no Cinema do Fly: Unauthorized»): chamada de dentro do service worker sai
   «de fora» do Fly e o Chrome não manda o cookie de login (SameSite) → 401. Agora toda chamada ao Fly roda DENTRO de uma aba do
   studio.flymedia.ai (a que já estiver aberta; se não tiver, abre uma em segundo plano), como o próprio site faz. */
async function abaDoFly() {
  const abas = await chrome.tabs.query({ url: "https://studio.flymedia.ai/*" });
  const pronta = abas.find((t) => t.status === "complete") || abas[0];
  if (pronta) return pronta.id;
  const nova = await chrome.tabs.create({ url: "https://studio.flymedia.ai/", active: false });
  await new Promise((ok) => { const f = (id, info) => { if (id === nova.id && info.status === "complete") { chrome.tabs.onUpdated.removeListener(f); ok(); } }; chrome.tabs.onUpdated.addListener(f); setTimeout(ok, 20000); });
  return nova.id;
}
async function noFly(func, args) {
  const tabId = await abaDoFly();
  const [r] = await chrome.scripting.executeScript({ target: { tabId }, world: "MAIN", func, args });
  return r && r.result;
}
async function flyApi(metodo, caminho, corpo) {
  if (!ROTAS.some(([m, re]) => m === metodo && re.test(caminho))) return { ok: false, status: 0, erro: "rota não liberada: " + metodo + " " + caminho };
  return noFly(async (API, metodo, caminho, corpo) => {
    const vai = () => fetch(API + caminho, { method: metodo, credentials: "include", headers: corpo ? { "Content-Type": "application/json" } : {}, body: corpo ? JSON.stringify(corpo) : undefined });
    let r = await vai();
    if (r.status === 401) { await fetch(API + "/v1/auth/session/refresh", { method: "POST", credentials: "include" }).catch(() => {}); r = await vai(); }
    const txt = await r.text();
    let dados = null; try { dados = txt ? JSON.parse(txt) : null; } catch (e) { dados = txt.slice(0, 500); }
    return r.ok ? { ok: true, status: r.status, dados } : { ok: false, status: r.status, erro: (dados && (dados.message || dados.error)) || ("HTTP " + r.status), dados };
  }, [FLY_API, metodo, caminho, corpo || null]);
}
const paraDataUrl = (b) => new Promise((ok, falha) => { const fr = new FileReader(); fr.onload = () => ok(fr.result); fr.onerror = () => falha(fr.error); fr.readAsDataURL(b); });
// imagem de referência (link do Fly X-tudo ou data: da página) → biblioteca do Fly → {type, uid}; guardada por link pra não subir 2×
async function subirRef(url, nome) {
  const chave = "flyref:" + url.slice(0, 300);
  if (!url.startsWith("data:")) { const g = await chrome.storage.local.get(chave); if (g[chave]) return { ok: true, dados: g[chave], cache: true }; }
  const blob = await (await fetch(url)).blob();
  const dataUrl = await paraDataUrl(blob);
  const res = await noFly(async (API, IP, dataUrl, nome) => {
    const blob = await (await fetch(dataUrl)).blob();
    const tipo = blob.type || "image/jpeg";
    const ext = (tipo.split("/")[1] || "jpg").replace("jpeg", "jpg").replace(/[^a-z0-9]/g, "");
    const pre = await fetch(API + "/v1/uploads/presigned-url", { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ mimeType: tipo, fileSize: blob.size, extension: ext }) });
    if (!pre.ok) return { ok: false, status: pre.status, erro: "presigned " + pre.status };
    const { uploadUrl, tempKey } = await pre.json();
    const put = await fetch(uploadUrl, { method: "PUT", body: blob, headers: { "Content-Type": tipo } });
    if (!put.ok) return { ok: false, status: put.status, erro: "upload " + put.status };
    const conf = await fetch(API + `/v1/ips/${IP}/libraries/assets/confirm`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tempKey, filename: (nome || "ref") + "." + ext }) });
    if (!conf.ok) return { ok: false, status: conf.status, erro: "confirm " + conf.status };
    const o = await conf.json();
    return { ok: true, dados: { type: o.type, uid: o.uid, previewUrl: o.previewUrl || null } };
  }, [FLY_API, FLY_IP, dataUrl, nome || "ref"]);
  if (res && res.ok && !url.startsWith("data:")) await chrome.storage.local.set({ [chave]: res.dados });
  return res || { ok: false, erro: "a aba do Fly não respondeu" };
}
// a saída de uma geração (mídia do Fly, que só abre com o login) → data: pra página subir pro Fly X-tudo
async function baixar(url) {
  if (!/^https:\/\/media\.studio\.flymedia\.ai\//.test(url)) return { ok: false, erro: "só mídia do Fly Studio" };
  return (await noFly(async (API, IP, url) => {
    await fetch(API + `/v1/ips/${IP}/media-cookies`, { method: "POST", credentials: "include" }).catch(() => {});
    const r = await fetch(url, { credentials: "include" });
    if (!r.ok) return { ok: false, status: r.status, erro: "mídia " + r.status };
    const b = await r.blob();
    const dataUrl = await new Promise((ok, falha) => { const fr = new FileReader(); fr.onload = () => ok(fr.result); fr.onerror = () => falha(fr.error); fr.readAsDataURL(b); });
    return { ok: true, dados: { dataUrl, tipo: b.type, tamanho: b.size } };
  }, [FLY_API, FLY_IP, url])) || { ok: false, erro: "a aba do Fly não respondeu" };
}
chrome.runtime.onMessage.addListener((msg, quem, responder) => {
  if (!msg || msg.tipo !== "fly-ponte") return;
  let origem = "";
  try { origem = quem.origin || new URL(quem.url).origin; } catch (e) {}
  if (!ORIGENS_FX.includes(origem)) { responder({ ok: false, erro: "origem não liberada: " + origem }); return; }
  const a = msg.args || {};
  const fazer = msg.op === "api" ? flyApi(a.metodo, a.caminho, a.corpo)
    : msg.op === "subirRef" ? subirRef(String(a.url || ""), a.nome)
    : msg.op === "baixar" ? baixar(String(a.url || ""))
    : msg.op === "ola" ? flyApi("GET", "/v1/auth/session/verify")
    : Promise.resolve({ ok: false, erro: "op desconhecida" });
  fazer.then(responder, (e) => responder({ ok: false, erro: String(e && e.message || e) }));
  return true;
});
