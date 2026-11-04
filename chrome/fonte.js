// Kakashi — olho no Chrome (04/11/2026): roda no MUNDO DA PÁGINA, onde o React/Vue/Svelte/Angular deixam a marca no elemento.
// Responde ao olho.js com o componente e, quando o app está em modo de desenvolvimento (localhost), o arquivo:linha do código.
// Só lê; não mexe na página.
(() => {
  const nomeDe = t => t && (t.displayName || t.name || (t.render && (t.render.displayName || t.render.name)) ||
                            (t.type && (t.type.displayName || t.type.name))) || "";

  function linhaDaPilha(pilha) {
    // React 19 não tem mais _debugSource: a pilha de quem criou o elemento diz o arquivo (pula as linhas do próprio React)
    for (const l of String(pilha || "").split("\n").slice(1)) {
      const m = l.match(/\(?((?:https?|file|webpack|vite)[^\s()]*?):(\d+):(\d+)\)?\s*$/);
      if (m && !/node_modules|react-dom|react\.|jsx-dev-runtime|chunk-/.test(m[1])) return m[1].replace(/\?[^:]*$/, "") + ":" + m[2];
    }
    return "";
  }

  function react(el) {
    let chave = null;
    for (let e = el, n = 0; e && n < 8 && !chave; e = e.parentElement, n++) {
      chave = Object.keys(e).find(k => k.startsWith("__reactFiber$") || k.startsWith("__reactInternalInstance$"));
      if (chave) el = e;
    }
    if (!chave) return null;
    const comps = []; let arquivo = "";
    for (let f = el[chave], n = 0; f && n < 60 && comps.length < 5; f = f.return, n++) {
      if (!arquivo && f._debugSource) arquivo = f._debugSource.fileName + ":" + f._debugSource.lineNumber;
      if (!arquivo && f._debugStack) arquivo = linhaDaPilha(f._debugStack.stack);
      if (typeof f.type === "function" || (f.type && typeof f.type === "object")) {
        const nome = nomeDe(f.type);
        if (nome && !comps.includes(nome)) comps.push(nome);
      }
    }
    return {framework: "React", componentes: comps, arquivo};
  }

  function vue(el) {
    for (let e = el, n = 0; e && n < 8; e = e.parentElement, n++) {
      const c = e.__vueParentComponent;
      if (c) {
        const comps = [];
        for (let i = c; i && comps.length < 5; i = i.parent) {
          const nome = i.type && (i.type.name || i.type.__name);
          if (nome) comps.push(nome);
        }
        return {framework: "Vue", componentes: comps, arquivo: (c.type && c.type.__file) || ""};
      }
      if (e.__vue__) {
        const o = e.__vue__.$options || {};
        return {framework: "Vue 2", componentes: [o.name || o._componentTag || ""].filter(Boolean), arquivo: o.__file || ""};
      }
    }
    return null;
  }

  function svelte(el) {
    for (let e = el, n = 0; e && n < 8; e = e.parentElement, n++) {
      const m = e.__svelte_meta;
      if (m && m.loc) return {framework: "Svelte", componentes: [], arquivo: m.loc.file + ":" + m.loc.line};
    }
    return null;
  }

  function angular(el) {
    try {
      const ng = window.ng;
      if (!ng || !ng.getComponent) return null;
      for (let e = el, n = 0; e && n < 12; e = e.parentElement, n++) {
        const c = ng.getComponent(e);
        if (c) return {framework: "Angular", componentes: [c.constructor.name], arquivo: ""};
      }
    } catch (e) {}
    return null;
  }

  function marcas(el) {
    // ferramentas de build que já escrevem a origem no HTML (data-source, data-inspector-*, data-loc, data-component, data-testid)
    const achou = {};
    for (let e = el, n = 0; e && n < 6; e = e.parentElement, n++) {
      for (const a of e.attributes || []) {
        if (/^data-.*(source|inspector|loc|file|component|testid|test-id|cy)/i.test(a.name) && !(a.name in achou))
          achou[a.name] = String(a.value).slice(0, 160);
      }
    }
    return Object.keys(achou).length ? achou : null;
  }

  window.addEventListener("kakashi:fonte", ev => {
    let r = null;
    try {
      const p = JSON.parse(ev.detail);
      const el = document.elementFromPoint(p.x, p.y);
      if (el) {
        r = react(el) || vue(el) || svelte(el) || angular(el) || {};
        const m = marcas(el);
        if (m) r.marcas = m;
        if (!Object.keys(r).length) r = null;
      }
    } catch (e) {}
    window.dispatchEvent(new CustomEvent("kakashi:fonte-resposta", {detail: JSON.stringify(r)}));
  });
})();
