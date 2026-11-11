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

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setFallo(null);
    setOrden(null);
    if (!id.trim()) { setFallo('El identificador de la orden es obligatorio.'); return; }
    try {
      setOrden(await send<Orden>('GET', `/api/intervenciones/orden-de-trabajo/${id.trim()}`));
    } catch (err) {
      setFallo(mensajeDeError(err));
    }
  }

  return (
    <section aria-label="Consulta de orden de trabajo">
      <form onSubmit={onSubmit} aria-label="Consultar orden de trabajo">
        <h3>Consultar orden de trabajo</h3>
        <label>Identificador de la orden<input value={id} onChange={(e) => setId(e.target.value)} /></label>
        <button type="submit">Consultar</button>
      </form>
      {fallo && <p role="alert">{fallo}</p>}
      {orden && (
        <dl>
          <dt>Dron</dt><dd>{orden.dronId}</dd>
          <dt>Tipo</dt><dd>{orden.tipo}</dd>
          <dt>Estado</dt><dd>{orden.estado}</dd>
          <dt>Técnico</dt><dd>{orden.tecnico ?? 'Sin asignar'}</dd>
          <dt>Horas hombre</dt><dd>{orden.horasHombre}</dd>
          <dt>Tareas</dt><dd>{orden.tareas.map((t) => `${t.descripcion}: ${t.resultado}`).join('; ') || 'Ninguna'}</dd>
          <dt>Consumos</dt><dd>{orden.consumos.map((c) => `${c.referencia} ×${c.cantidad}`).join('; ') || 'Ninguno'}</dd>
          <dt>Hallazgos</dt><dd>{orden.hallazgos.map((h) => h.descripcion).join('; ') || 'Ninguno'}</dd>
        </dl>
      )}
    </section>
  );
}
