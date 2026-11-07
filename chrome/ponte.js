// Ponte Fly X-tudo → Fly Studio (06/11/2026, ele: «pra não gastar o dinheiro da ARDI... a gente gasta o do Fly Studio e fica tudo lá
// já também... aqui vai ser tipo só a interface que eu uso... como se fosse um MCP» · «Pode começar»).
// Roda SÓ nas páginas do Fly X-tudo (site e bancada). A página pede por window.postMessage({fxPonte:"pede", id, op, args}); isto aqui
// repassa pro fundo da extensão, que fala com a API do Fly Studio com o login do Chrome, e devolve {fxPonte:"resposta", id, ...}.
// Nenhuma outra página chega aqui (matches do manifest) e o fundo confere a origem de novo e só deixa as rotas de gerar/ler do IP Plexus.
(function () {
  /* the extension reloads itself when its files change (fundo.js); the old copy of this script stays in the page with a dead context,
     so it steps aside and the fresh one (put in by fundo.js) answers — otherwise the page got «Extension context invalidated» */
  /* only the newest copy answers (its token on <html>): two live copies would send every request twice — a generation paid twice */
  const EU = Math.random().toString(36).slice(2);
  const raiz = () => document.documentElement;
  if (raiz()) raiz().dataset.fxPonte = EU;
  const vivo = () => { try { return !!(chrome.runtime && chrome.runtime.id) && (!raiz() || raiz().dataset.fxPonte === EU); } catch (e) { return false; } };
  const VERSAO = (() => { try { return chrome.runtime.getManifest().version; } catch (e) { return "?"; } })();
  const ola = () => window.postMessage({ fxPonte: "ola", versao: VERSAO }, location.origin);
  window.addEventListener("message", function ouvir(e) {
    if (!vivo()) { window.removeEventListener("message", ouvir); return; }
    if (e.source !== window || e.origin !== location.origin) return;
    const d = e.data;
    if (!d || typeof d !== "object") return;
    if (d.fxPonte === "oi?") return ola();
    if (d.fxPonte !== "pede" || !d.id || !d.op) return;
    try {
      chrome.runtime.sendMessage({ tipo: "fly-ponte", op: d.op, args: d.args || {} }, (r) => {
        const erro = chrome.runtime.lastError;
        window.postMessage(Object.assign({ fxPonte: "resposta", id: d.id }, erro ? { ok: false, erro: erro.message } : r || { ok: false, erro: "sem resposta" }), location.origin);
      });
    } catch (err) {
      window.postMessage({ fxPonte: "resposta", id: d.id, ok: false, erro: String(err && err.message || err) }, location.origin);
    }
  });
  ola();
})();
