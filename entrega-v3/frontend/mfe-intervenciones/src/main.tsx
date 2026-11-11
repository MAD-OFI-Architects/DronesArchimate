import { createRoot, type Root } from 'react-dom/client';
import { App } from './App';
import css from './styles.css?inline';

class Element extends HTMLElement {
  private root?: Root;
  connectedCallback() {
    const shadow = this.shadowRoot ?? this.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = css;
    const mount = document.createElement('div');
    shadow.replaceChildren(style, mount);
    this.root = createRoot(mount);
    this.root.render(<App role={this.getAttribute('data-role') ?? ''} />);
  }
  disconnectedCallback() { this.root?.unmount(); }
}
if (!customElements.get('mfe-intervenciones')) customElements.define('mfe-intervenciones', Element);
