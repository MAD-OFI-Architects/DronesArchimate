import { useState, type FormEvent } from 'react';
import { send, mensajeDeError } from '../api';

export interface ConsultaViewProps { titulo: string; etiqueta: string; ruta: (id: string) => string }

export function ConsultaView({ titulo, etiqueta, ruta }: ConsultaViewProps) {
  const [id, setId] = useState('');
  const [datos, setDatos] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null); setDatos(null);
    if (!id.trim()) { setError(`${etiqueta} es obligatorio`); return; }
    try { setDatos(await send<Record<string, unknown>>('GET', ruta(id.trim()))); }
    catch (err) { setError(mensajeDeError(err)); }
  }
  return (
    <section aria-label={titulo}>
      <h3>{titulo}</h3>
      <form onSubmit={onSubmit} aria-label={`Buscar ${titulo}`}>
        <label>{etiqueta}<input value={id} onChange={(e) => setId(e.target.value)} /></label>
        <button type="submit">Consultar</button>
      </form>
      {error && <p role="alert">{error}</p>}
      {datos && <dl>{Object.entries(datos).map(([k, v]) => (<div key={k}><dt>{k}</dt><dd>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</dd></div>))}</dl>}
    </section>
  );
}
