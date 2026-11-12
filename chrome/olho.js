// Kakashi — olho no Chrome (04/11/2026). Pedido dele: «colocasse o mouse do Kakashi nas coisas do PC, do Chrome, pelo código...
// pelo código fonte, pra saber o elemento, ajudar esse rastro do mouse».
// O Windows (UIA) só diz «título FLY HUB»; daqui sai o elemento de verdade: a tag de abertura do HTML, o seletor, o texto, o link,
// a imagem e, em app local feito em React/Vue/Svelte, o componente e o arquivo:linha do código (fonte.js, no mundo da página).
// Mesmo ritmo do olho do Windows (kakashi.pyw, Vigia): na pausa do mouse (>0,8 s depois de andar >25 px) e em todo clique.
// Nunca lê o que está digitado num campo (value) nem campo de senha.
(() => {
  const PAUSA = 800, ANDAR = 25;
  let x = 0, y = 0, sx = 0, sy = 0, andou = 0, relogio = null, ult = null;

  function curto(s, n) {
    s = (s || "").replace(/\s+/g, " ").trim();
    return s.length > n ? s.slice(0, n - 1) + "…" : s;
  }

  function tagAbertura(el) {
    const c = el.cloneNode(false);
    c.removeAttribute("value");                       // o que foi digitado não sai daqui
    let h = c.outerHTML || "";
    const i = h.indexOf(">");
    return curto(i >= 0 ? h.slice(0, i + 1) : h, 300);
  }

  function seletor(el) {
    const partes = [];
    for (let e = el; e && e.nodeType === 1 && partes.length < 6; e = e.parentElement) {
      if (e.id && !/\d{4,}/.test(e.id)) { partes.unshift("#" + CSS.escape(e.id)); break; }
      let p = e.tagName.toLowerCase();
      const cls = [...e.classList].filter(k => k.length < 30 && !/[0-9a-f]{6,}|^css-|^sc-/.test(k)).slice(0, 2);
      if (cls.length) p += "." + cls.map(k => CSS.escape(k)).join(".");
      const pai = e.parentElement;
      if (pai) {
        const iguais = [...pai.children].filter(f => f.tagName === e.tagName);
        if (iguais.length > 1) p += ":nth-of-type(" + (iguais.indexOf(e) + 1) + ")";
      }
      partes.unshift(p);
    }
    return partes.join(" > ");
  }

  function imagemDe(el) {
    for (let e = el, n = 0; e && n < 3; e = e.parentElement, n++) {
      if (e.tagName === "IMG") return e.currentSrc || e.src;
      if (e.tagName === "VIDEO") return e.currentSrc || e.src || e.poster;
      if (e.tagName === "image" || e.tagName === "IMAGE") return e.getAttribute("href");
      const bg = getComputedStyle(e).backgroundImage;
      const m = bg && bg.match(/url\(["']?(.*?)["']?\)/);
      if (m) return m[1];
    }
    return "";
  }

  function fonteDaPagina(cx, cy) {
    // o fonte.js (mundo da página) é quem enxerga o React/Vue/Svelte; a conversa é síncrona por evento
    let r = null;
    const ouvir = ev => { try { r = JSON.parse(ev.detail); } catch (e) {} };
    window.addEventListener("kakashi:fonte-resposta", ouvir, {once: true});
    window.dispatchEvent(new CustomEvent("kakashi:fonte", {detail: JSON.stringify({x: cx, y: cy})}));
    window.removeEventListener("kakashi:fonte-resposta", ouvir);
    return r;
  }

  function descrever(motivo, cx, cy, tx, ty) {
    const el = document.elementFromPoint(cx, cy);
    if (!el) return null;
    const ret = el.getBoundingClientRect();
    const senha = el.tagName === "INPUT" && (el.type || "").toLowerCase() === "password";
    const campo = el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable;
    const link = el.closest("a[href]");
    const d = {
      motivo, url: location.href, titulo: curto(document.title, 120), topo: window === window.top,
      tag: el.tagName.toLowerCase(), id: el.id || "", classes: curto(typeof el.className === "string" ? el.className : "", 160),
      html: tagAbertura(el), seletor: seletor(el),
      texto: campo ? "" : curto(el.innerText || el.textContent, 200),
      rotulo: curto(el.getAttribute("aria-label") || el.getAttribute("title") || el.getAttribute("alt") ||
                    el.getAttribute("placeholder") || el.getAttribute("name") || "", 120),
      papel: el.getAttribute("role") || "", link: link ? link.href : "", imagem: curto(imagemDe(el), 400),
      ret: [Math.round(ret.left), Math.round(ret.top), Math.round(ret.width), Math.round(ret.height)],
      cx: Math.round(cx), cy: Math.round(cy), sx: Math.round(tx), sy: Math.round(ty), dpr: window.devicePixelRatio,
    };
    if (senha) d.senha = true;
    if (!d.texto && !campo && el.parentElement) d.texto_pai = curto(el.parentElement.innerText, 160);
    const f = fonteDaPagina(cx, cy);
    if (f) d.fonte = f;
    return d;
  }

  function relatar(motivo, cx, cy, tx, ty) {
    try {
      chrome.runtime.sendMessage({tipo: "gravando?"}, r => {
        if (chrome.runtime.lastError || !r || !r.gravando) return;
        const d = descrever(motivo, cx, cy, tx, ty);
        if (!d) return;
        const chave = motivo + "|" + d.seletor + "|" + d.cx + "|" + d.cy;
        if (chave === ult) return;
        ult = chave;
        chrome.runtime.sendMessage({tipo: "elemento", dados: d});
      });
    } catch (e) { /* extensão recarregada: esta página fica sem olho até recarregar */ }
  }

  // a extensão se recarrega sozinha e entra de novo nas guias abertas (fundo.js): pode sobrar o olho de antes (no mesmo mundo ou
  // num mundo órfão da versão velha). O novo avisa por um evento da janela, que chega em todos os mundos, e os de antes se desligam.
  const eu = Math.random().toString(36).slice(2);
  let ligado = true;
  window.dispatchEvent(new CustomEvent("kakashi:olho-novo", {detail: eu}));
  const sair = ev => {
    if (ev.detail === eu) return;
    ligado = false; clearTimeout(relogio);
    removeEventListener("mousemove", mexeu, {capture: true}); removeEventListener("pointerdown", clicou, {capture: true});
    removeEventListener("kakashi:olho-novo", sair);
  };
  addEventListener("kakashi:olho-novo", sair);
  const mexeu = ev => {
    if (!ligado) return;
    andou += Math.abs(ev.clientX - x) + Math.abs(ev.clientY - y);
    x = ev.clientX; y = ev.clientY; sx = ev.screenX; sy = ev.screenY;
    clearTimeout(relogio);
    relogio = setTimeout(() => {
      if (andou > ANDAR) { andou = 0; relatar("parou", x, y, sx, sy); }
    }, PAUSA);
  };
  const clicou = ev => {
    if (ligado) relatar(ev.button === 2 ? "clique_direito" : "clique", ev.clientX, ev.clientY, ev.screenX, ev.screenY);
  };
  addEventListener("mousemove", mexeu, {capture: true, passive: true});
  addEventListener("pointerdown", clicou, {capture: true, passive: true});

  // KAKASHI 3.0 (12/11/2026): «o que está debaixo da ponta do desenho?» — o fundo.js pergunta com o ponto da TELA (DIP); só a
  // página de cima responde. Ponto da tela → ponto da página: pelo último mouse que passou aqui (tela = origem + página × zoom); sem
  // nenhum, pela moldura da janela (estimativa).
  let ultMouse = null;               // o último mouse aqui: tela (screenX/Y, DIP) e página (clientX/Y, px CSS)
  addEventListener("mousemove", ev => { ultMouse = [ev.screenX, ev.screenY, ev.clientX, ev.clientY]; }, {capture: true, passive: true});
  const perguntaPonto = (msg, quem, responder) => {
    if (!ligado || window !== window.top || !msg || msg.tipo !== "descrever-ponto") return;
    const zoom = window.devicePixelRatio / (msg.escala || 1);          // o zoom da página (Ctrl + / Ctrl -)
    const borda = (window.outerWidth - window.innerWidth * zoom) / 2;
    const o = ultMouse ? {x: ultMouse[0] - ultMouse[2] * zoom, y: ultMouse[1] - ultMouse[3] * zoom}
                       : {x: window.screenX + borda, y: window.screenY + window.outerHeight - window.innerHeight * zoom - borda};
    const cx = (msg.x - o.x) / zoom, cy = (msg.y - o.y) / zoom;
    if (cx < 0 || cy < 0 || cx > window.innerWidth || cy > window.innerHeight) { responder({dados: null}); return; }
    responder({dados: descrever("traco", cx, cy, msg.x, msg.y)});
  };
  chrome.runtime.onMessage.addListener(perguntaPonto);
  addEventListener("kakashi:olho-novo", ev => { if (ev.detail !== eu) chrome.runtime.onMessage.removeListener(perguntaPonto); });
})();
