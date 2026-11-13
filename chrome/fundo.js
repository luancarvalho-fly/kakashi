// Kakashi — olho no Chrome (04/11/2026). O fundo da extensão: recebe o elemento que o olho.js achou debaixo do mouse e manda pro
// Kakashi (127.0.0.1:7816, POST /chrome). Só manda enquanto o Kakashi está gravando (GET /status, guardado por 2 s); Kakashi fechado
// ou parado = nada sai do Chrome. Nada vai pra fora do PC.
//
// SE RECARREGA SOZINHA (04/11, ele: «Pode fazer», sobre o buraco do ATUALIZAR): o ATUALIZAR do Kakashi troca os arquivos desta pasta,
// mas o Chrome segue rodando o código velho. Na hora em que esta versão entra (instalada, recarregada ou Chrome aberto), guardo a
// impressão (SHA-256) dos arquivos como estão no disco; a cada minuto comparo de novo: mudou = chrome.runtime.reload(). Ao entrar,
// ponho o olho também nas guias que já estavam abertas (sem precisar de F5). A impressão fica no chrome.storage.local («carregada»).
const KAKASHI = "http://127.0.0.1:7816";
const ARQUIVOS = ["manifest.json", "fundo.js", "olho.js", "fonte.js", "ponte.js", "opcoes.html", "opcoes.js"];
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
  // 11/11: o token da ponte nasce aqui se ainda não existe (as opções mostram, copiam e trocam); sem ele a ponte recusa tudo
  try {
    const g = await chrome.storage.local.get("ponteSegredo");
    if (!g.ponteSegredo) {
      const b = new Uint8Array(32); crypto.getRandomValues(b);
      await chrome.storage.local.set({ ponteSegredo: btoa(String.fromCharCode(...b)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "") });
    }
  } catch (e) {}
  await entrarNasGuias();
}

chrome.runtime.onInstalled.addListener(() => { entrou(); });      // instalada ou recarregada (inclusive pelo reload acima)
chrome.runtime.onStartup.addListener(() => { entrou(); });        // Chrome aberto: o código que roda é o do disco agora
chrome.alarms.create("conferir", {periodInMinutes: 1});
chrome.alarms.onAlarm.addListener(a => { if (a.name === "conferir") { conferir(); gravando(); } });   // 3.0: acorda o vigia do desenho


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
  // 12/11 (espelho do PLAY no Fly X-tudo): a lista vem em páginas de 20; a seguinte pede ?cursor=<token> — só esse parâmetro é aceito
  ["GET", new RegExp(`^/v1/ips/${FLY_IP}/canvas/${U}/predictions([?]cursor=[A-Za-z0-9_%=-]{1,400})?$`)],
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
/* 11/11/2026 (auditoria): o subirRef buscava QUALQUER endereço com a força da extensão (sem CORS) e devolvia o resultado pela biblioteca
   do Fly — dava pra puxar os apps locais do PC, o Kakashi ou a rede de casa. Agora só: data: da página, o próprio X-tudo que pediu, ou https de fora
   (o armazenamento da ARDI etc.). Nunca o PC, a rede local nem o Tailscale; e se um link de fora redirecionar pra dentro, não sobe. */
function enderecoDeDentro(host) {
  host = String(host || "").toLowerCase().replace(/^\[|\]$/g, "");
  if (!host || host === "localhost" || host.endsWith(".localhost") || host.endsWith(".local") || host.endsWith(".internal") || host.endsWith(".ts.net")) return true;
  if (!host.includes(".") && !host.includes(":")) return true;                      // nome sem domínio = máquina da rede
  const m = host.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
  if (m) {
    const [a, b] = [Number(m[1]), Number(m[2])];
    return a === 0 || a === 10 || a === 127 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127) || a >= 224;
  }
  if (host.includes(":")) return host === "::" || host === "::1" || /^(fc|fd|fe8|fe9|fea|feb)/.test(host) || host.startsWith("::ffff:");
  return false;
}
function refPermitida(url, origemPagina) {
  if (url.startsWith("data:")) return true;
  let u; try { u = new URL(url); } catch (e) { return false; }
  if (u.origin === origemPagina) return true;                                       // o próprio X-tudo que pediu (inclusive o do PC)
  return u.protocol === "https:" && !enderecoDeDentro(u.hostname);
}
// imagem de referência (link do Fly X-tudo ou data: da página) → biblioteca do Fly → {type, uid}; guardada por link pra não subir 2×
async function subirRef(url, nome, origemPagina) {
  if (!refPermitida(url, origemPagina)) return { ok: false, erro: "referência fora do permitido (só data:, o próprio X-tudo ou https de fora do PC)" };
  const chave = "flyref:" + url.slice(0, 300);
  if (!url.startsWith("data:")) { const g = await chrome.storage.local.get(chave); if (g[chave]) return { ok: true, dados: g[chave], cache: true }; }
  /* 12/11/2026 (Kakashi 05:42 [5:30], «Não consegui enviar membro do comando»): a picture of 16,6 MB went whole as data: in the
     executeScript arguments and the Fly's tab gave nothing back. A link from outside the PC (ARDI's storage, open to any site) is now
     fetched by the Fly's tab itself; only data: and the X-tudo's own links still travel inside the message */
  const deFora = !url.startsWith("data:") && (() => { try { return new URL(url).origin !== origemPagina; } catch (e) { return false; } })();
  let dataUrl = null;
  if (deFora) {
    const cab = await fetch(url, { method: "HEAD" });
    if (cab.url && !refPermitida(cab.url, origemPagina)) return { ok: false, erro: "a referência redirecionou pra um endereço de dentro do PC" };
  } else {
    const resp = await fetch(url);
    if (resp.url && !url.startsWith("data:") && !refPermitida(resp.url, origemPagina)) return { ok: false, erro: "a referência redirecionou pra um endereço de dentro do PC" };
    dataUrl = await paraDataUrl(await resp.blob());
  }
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
  }, [FLY_API, FLY_IP, dataUrl || url, nome || "ref"]);
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
/* 13/11/2026 — SEPARADOR (botão «Separar» da bancada de Sonoplastia do Fly X-tudo). Ele: «sim, separar unitário pela geração» · «vê se
   não tem nenhuma vulnerabilidade, igual o Rolf tinha reportado... vai rodar no meu PC aqui... só para o Plexus, e pra minha utilização».
   O pedido vem SÓ do Fly X-tudo, com o token da ponte (conferido abaixo, igual às rotas do Fly), e eu repasso pro servidor local
   127.0.0.1:7817 (apps\TANDERA\separador), que só existe no PC dele: nos outros PCs não tem servidor → «indisponível» e o botão nem
   aparece. O servidor confere Host, a Origin desta extensão e o segredo dele (pareado aqui uma vez, guardado em chrome.storage.local,
   nunca vai pra página). Antes de repassar eu também confiro: fonte só do armazenamento da ARDI ou da pasta /x-studio/vlogs do site,
   envio só pros endereços assinados do mesmo armazenamento. Nada de URL ou caminho livre. */
const SEPARADOR = "http://127.0.0.1:7817";
const ARMAZEM_ARDI = "uppinfbftdvxulabfwvy.supabase.co";
function fonteSeparavel(src) {
  if (typeof src !== "string" || src.length > 1000) return false;
  if (src.startsWith("/x-studio/vlogs/")) return !/(^|[\\/])\.\.([\\/]|$)/.test(decodeURIComponent(src)) && /\.(m4a|mp4|wav|flac)(\?|$)/i.test(src);
  let u; try { u = new URL(src); } catch (e) { return false; }
  return u.protocol === "https:" && u.hostname === ARMAZEM_ARDI && !u.port && !u.username && u.pathname.startsWith("/storage/v1/object/public/media/") && !u.pathname.includes("..");
}
function envioPermitido(url) {
  let u; try { u = new URL(url); } catch (e) { return false; }
  return u.protocol === "https:" && u.hostname === ARMAZEM_ARDI && !u.port && !u.username && u.pathname.startsWith("/storage/v1/object/") && !u.pathname.includes("..");
}
async function separadorSegredo(renovar) {
  const g = await chrome.storage.local.get("separadorSegredo");
  if (g.separadorSegredo && !renovar) return g.separadorSegredo;
  // tudo POST com JSON: num GET o Chrome não manda o Origin da extensão, e é ele que o separador confere
  const r = await fetch(SEPARADOR + "/par", { method: "POST", cache: "no-store", headers: { "Content-Type": "application/json" }, body: "{}" });
  const j = r.ok ? await r.json() : null;
  if (!j || typeof j.segredo !== "string") throw new Error("o separador não pareou");
  await chrome.storage.local.set({ separadorSegredo: j.segredo });
  return j.segredo;
}
async function separador(caminho, corpo) {
  const vai = async (renovar) => fetch(SEPARADOR + caminho, { method: "POST", cache: "no-store", headers: { "X-Separador": await separadorSegredo(renovar), "Content-Type": "application/json" }, body: JSON.stringify(corpo || {}) });
  let r;
  try { r = await vai(false); if (r.status === 401) r = await vai(true); }
  catch (e) { return { ok: false, erro: "indisponível: o separador só roda no PC do Luan, com o servidor dele ligado" }; }
  let j = null; try { j = await r.json(); } catch (e) {}
  return r.ok && j && j.ok ? { ok: true, dados: j } : { ok: false, status: r.status, erro: (j && j.erro) || ("separador " + r.status) };
}
function separar(a) {
  if (!fonteSeparavel(a.src)) return Promise.resolve({ ok: false, erro: "fonte fora do permitido (só geração do armazenamento da ARDI ou som do próprio site)" });
  const ups = a.uploads || {};
  if (!["voz", "musica", "efeitos"].every((k) => typeof ups[k] === "string" && envioPermitido(ups[k]))) return Promise.resolve({ ok: false, erro: "envio fora do armazenamento da ARDI" });
  return separador("/separar", { src: a.src, uploads: { voz: ups.voz, musica: ups.musica, efeitos: ups.efeitos } });
}
/* 11/11/2026 (auditoria; ele: «Pode começar»): SEGREDO DA PONTE. Só a origem não bastava — qualquer código que rodasse no X-tudo (deploy
   comprometido, dependência maliciosa, XSS) ou qualquer programa na porta 3007 do PC gastava o crédito do Fly em nome dele. Agora todo
   pedido precisa trazer o token das opções da extensão (opcoes.html, chrome.storage.local «ponteSegredo», 32 bytes aleatórios). Vazio ou
   diferente = recusa, inclusive o «ola». O token nunca vai pra log, pra mensagem de erro nem de volta pra página. */
const CHAVE_SEGREDO = "ponteSegredo";
function mesmoSegredo(guardado, veio) {                // tempo constante: confere o tamanho e todos os caracteres, sem sair no primeiro erro
  if (typeof guardado !== "string" || typeof veio !== "string" || !guardado) return false;
  let dif = guardado.length ^ veio.length;
  for (let i = 0; i < guardado.length; i++) dif |= guardado.charCodeAt(i) ^ (i < veio.length ? veio.charCodeAt(i) : 0);
  return dif === 0;
}
// o content script (ponte.js, olho.js) não precisa ler o storage: fica só pro fundo e pras opções (onde o Chrome deixar)
try { const p = chrome.storage.local.setAccessLevel && chrome.storage.local.setAccessLevel({ accessLevel: "TRUSTED_CONTEXTS" }); if (p && p.catch) p.catch(() => {}); } catch (e) {}
chrome.runtime.onMessage.addListener((msg, quem, responder) => {
  if (!msg || msg.tipo !== "fly-ponte") return;
  let origem = "";
  try { origem = quem.origin || new URL(quem.url).origin; } catch (e) {}
  if (!ORIGENS_FX.includes(origem)) { responder({ ok: false, erro: "origem não liberada: " + origem }); return; }
  chrome.storage.local.get(CHAVE_SEGREDO).then((g) => {
    if (!mesmoSegredo(g[CHAVE_SEGREDO], msg.segredo)) { responder({ ok: false, erro: "segredo inválido" }); return; }
    const a = msg.args || {};
    const fazer = msg.op === "api" ? flyApi(a.metodo, a.caminho, a.corpo)
      : msg.op === "subirRef" ? subirRef(String(a.url || ""), a.nome, origem)
      : msg.op === "baixar" ? baixar(String(a.url || ""))
      : msg.op === "ola" ? flyApi("GET", "/v1/auth/session/verify")
      : msg.op === "separar-ola" ? separador("/ola")
      : msg.op === "separar" ? separar(a)
      : msg.op === "separar-estado" ? (/^[0-9a-f]{16}$/.test(String(a.job || "")) ? separador("/estado", { job: String(a.job) }) : Promise.resolve({ ok: false, erro: "job inválido" }))
      : Promise.resolve({ ok: false, erro: "op desconhecida" });
    fazer.then(responder, (e) => responder({ ok: false, erro: String(e && e.message || e) }));
  }, () => responder({ ok: false, erro: "segredo inválido" }));
  return true;
});
