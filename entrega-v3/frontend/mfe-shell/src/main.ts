interface Entry { tag: string; module: string; context: string; roles: string[] }
const outlet = document.getElementById('outlet')!;
const select = document.getElementById('role') as HTMLSelectElement;
const toast = document.getElementById('toast')!;

// Composición en tiempo de ejecución: el shell no conoce a los remotes en compilación, solo el manifiesto.
// Cada dominio es dueño de su remote; el rol elegido decide cuáles se muestran y qué formularios ve cada uno.
async function show(manifest: Entry[], role: string) {
  const mine = manifest.filter((m) => m.roles.includes(role));
  for (const m of mine) if (!customElements.get(m.tag)) await import(/* @vite-ignore */ m.module);
  outlet.replaceChildren(...mine.map((m) => Object.assign(document.createElement(m.tag), {}) as HTMLElement).map((el) => {
    el.setAttribute('data-role', role);
    return el;
  }));
}
async function boot() {
  const manifest: Entry[] = await (await fetch('/mfe-manifest.json')).json();
  const roles = [...new Set(manifest.flatMap((m) => m.roles))].sort();
  select.replaceChildren(...roles.map((r) => Object.assign(document.createElement('option'), { value: r, textContent: r })));
  select.addEventListener('change', () => show(manifest, select.value));
  window.addEventListener('mfe:notify', (e) => {
    toast.textContent = (e as CustomEvent).detail.message; toast.hidden = false; setTimeout(() => (toast.hidden = true), 3000);
  });
  if (roles.length) show(manifest, roles[0]);
}
boot();
