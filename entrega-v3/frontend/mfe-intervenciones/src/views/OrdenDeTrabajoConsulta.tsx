import { useState, type FormEvent } from 'react';
import { send } from '../api';
import { mensajeDeError } from '../reglas';

interface Orden {
  id: string; dronId: string; tipo: string; estado: string; tecnico?: string | null; horasHombre: number;
  tareas: { id: string; descripcion: string; resultado: string }[];
  consumos: { id: string; referencia: string; cantidad: number }[];
  hallazgos: { descripcion: string }[];
}

/** Vista de consulta de la orden de trabajo: GET /api/intervenciones/orden-de-trabajo/{id}. */
export function OrdenDeTrabajoConsulta() {
  const [id, setId] = useState('');
  const [orden, setOrden] = useState<Orden | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [consultando, setConsultando] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setFallo(null);
    setOrden(null);
    if (!id.trim()) { setFallo('El identificador de la orden es obligatorio.'); return; }
    try {
      setConsultando(true);
      setOrden(await send<Orden>('GET', `/api/intervenciones/orden-de-trabajo/${id.trim()}`));
    } catch (err) {
      setFallo(mensajeDeError(err));
    } finally {
      setConsultando(false);
    }
  }

  return (
    <section className="card" aria-label="Consulta de orden de trabajo">
      <form onSubmit={onSubmit} aria-label="Consultar orden de trabajo">
        <h3>Consultar orden de trabajo</h3>
        <label className="field">Identificador de la orden<input value={id} onChange={(e) => setId(e.target.value)} aria-invalid={Boolean(fallo && !id.trim())} /></label>
        <button type="submit" disabled={consultando}>{consultando ? 'Consultando…' : 'Consultar'}</button>
      </form>
      {fallo && <p role="alert">{fallo}</p>}
      {!orden && !fallo && <p className="empty">Ingresa el identificador de una orden para consultar su estado.</p>}
      {orden && <table className="table">
        <caption className="mfe-sub">Detalle de la orden de trabajo</caption>
        <tbody>
          <tr><th scope="row">Dron</th><td>{orden.dronId}</td></tr>
          <tr><th scope="row">Tipo</th><td>{orden.tipo}</td></tr>
          <tr><th scope="row">Estado</th><td><span className="badge">{orden.estado}</span></td></tr>
          <tr><th scope="row">Técnico</th><td>{orden.tecnico ?? 'Sin asignar'}</td></tr>
          <tr><th scope="row">Horas hombre</th><td>{orden.horasHombre}</td></tr>
          <tr><th scope="row">Tareas</th><td>{orden.tareas.map((t) => `${t.descripcion}: ${t.resultado}`).join('; ') || 'Ninguna'}</td></tr>
          <tr><th scope="row">Consumos</th><td>{orden.consumos.map((c) => `${c.referencia} ×${c.cantidad}`).join('; ') || 'Ninguno'}</td></tr>
          <tr><th scope="row">Hallazgos</th><td>{orden.hallazgos.map((h) => h.descripcion).join('; ') || 'Ninguno'}</td></tr>
        </tbody>
      </table>}
    </section>
  );
}
