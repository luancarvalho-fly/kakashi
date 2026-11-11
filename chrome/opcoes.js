// Token da ponte Fly X-tudo → Fly Studio (11/11/2026, auditoria de segurança; ele: «Pode começar»).
// 32 bytes de crypto.getRandomValues em base64url, guardados em chrome.storage.local («ponteSegredo»). O fundo.js recusa todo pedido da
// ponte que não trouxer este mesmo valor. Fica escondido até clicar em Mostrar; nunca vai pra log.
(() => {
  const CHAVE = "ponteSegredo";
  const el = (id) => document.getElementById(id);
  let valor = "", visivel = false;

  function novoToken() {
    const b = new Uint8Array(32);
    crypto.getRandomValues(b);
    return btoa(String.fromCharCode(...b)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function pintar() {
    el("token").textContent = valor ? (visivel ? valor : "•".repeat(43)) : "(nenhum)";
    el("mostrar").textContent = visivel ? "Esconder" : "Mostrar";
  }
  function avisar(t) { el("aviso").textContent = t; }

  async function carregar() {
    const g = await chrome.storage.local.get(CHAVE);
    valor = typeof g[CHAVE] === "string" ? g[CHAVE] : "";
    if (!valor) {                       // primeira vez: gera e guarda
      valor = novoToken();
      await chrome.storage.local.set({ [CHAVE]: valor });
      avisar("Token criado agora. Copie e cole no Fly X-tudo.");
    }
    pintar();
  }

  el("mostrar").addEventListener("click", () => { visivel = !visivel; pintar(); });
  el("copiar").addEventListener("click", async () => {
    if (!valor) return;
    try { await navigator.clipboard.writeText(valor); avisar("Copiado. Agora cole no Fly X-tudo."); }
    catch (e) { visivel = true; pintar(); avisar("Não consegui copiar sozinho: selecione o token acima e copie."); }
  });
  el("novo").addEventListener("click", async () => {
    if (!confirm("Gerar um token novo? O antigo para de valer na hora e o Fly X-tudo fica recusado até você colar o novo.")) return;
    valor = novoToken();
    await chrome.storage.local.set({ [CHAVE]: valor });
    visivel = false; pintar();
    avisar("Token novo criado. O antigo já não vale: copie e cole este no Fly X-tudo.");
  });
  chrome.storage.onChanged.addListener((mud, area) => {
    if (area === "local" && mud[CHAVE] && mud[CHAVE].newValue !== valor) { valor = mud[CHAVE].newValue || ""; pintar(); }
  });

  carregar();
})();
