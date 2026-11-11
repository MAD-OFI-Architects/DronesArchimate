import { useId, useState, type FormEvent } from 'react';
import { send, mensajeDeError, notify } from '../api';

export interface ConsultaViewProps { titulo: string; etiqueta: string; ruta: (id: string) => string; /** Ayuda corta bajo el campo: qué se escribe y de dónde sale. */ ayuda?: string }

export function ConsultaView({ titulo, etiqueta, ruta, ayuda }: ConsultaViewProps) {
  const uid = useId();
  const [id, setId] = useState('');
  const [datos, setDatos] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null); setDatos(null);
    if (!id.trim()) { setError(`${etiqueta} es obligatorio`); return; }
    try {
      setCargando(true);
      const resultado = await send<Record<string, unknown>>('GET', ruta(id.trim()));
      setDatos(resultado);
      notify(`${titulo}: consulta realizada`);
    } catch (err) { setError(mensajeDeError(err)); }
    finally { setCargando(false); }
  }
  return (
    <section className="card" aria-label={titulo}>
      <h3>{titulo}</h3>
      <form onSubmit={onSubmit} aria-label={`Buscar ${titulo}`}>
        <div className="campo"><label className="field">{etiqueta}<input value={id} aria-label={etiqueta} aria-invalid={!!error} aria-describedby={ayuda ? `${uid}-ayuda` : undefined}
          onChange={(e) => setId(e.target.value)} /></label>{ayuda && <small className="hint" id={`${uid}-ayuda`}>{ayuda}</small>}</div>
        <button className="btn" type="submit" disabled={cargando}>{cargando ? 'Consultando…' : 'Consultar'}</button>
      </form>
      {error && <p role="alert" className="alert">{error}</p>}
      {!datos && !error && <p className="empty">Ingresa un identificador para consultar.</p>}
      {datos && <ConsultaTabla datos={datos} />}
    </section>
  );
}

const ETIQUETAS: Record<string, string> = {
  referencia: 'Referencia', cantidad: 'Cantidad', stock_minimo: 'Stock mínimo',
  plazo_dias: 'Plazo de reposición (días)', disponible: 'Disponible', reservado: 'Reservado',
  estado: 'Estado', solicitud_id: 'Solicitud', orden_trabajo_id: 'Orden de trabajo',
  monto: 'Monto', nivel_aprobacion: 'Nivel de aprobación', cantidad_solicitada: 'Cantidad solicitada',
};

function etiqueta(campo: string): string {
  return ETIQUETAS[campo] ?? campo.replace(/_/g, ' ').replace(/^./, (c: string) => c.toUpperCase());
}

function valorLegible(valor: unknown): string {
  if (typeof valor === 'boolean') return valor ? 'Sí' : 'No';
  if (valor === null || valor === undefined || valor === '') return '—';
  return String(valor);
}

function ConsultaTabla({ datos }: { datos: Record<string, unknown> }) {
  const filas = Object.entries(datos).filter(([, valor]) => typeof valor !== 'object' || valor === null);
  return filas.length ? (
    <table className="table">
      <thead><tr><th>Dato</th><th>Valor</th></tr></thead>
      <tbody>{filas.map(([campo, valor]) => (
        <tr key={campo}><th scope="row">{etiqueta(campo)}</th><td>
          {campo === 'estado' ? <span className="badge">{valorLegible(valor)}</span> : valorLegible(valor)}
        </td></tr>
      ))}</tbody>
    </table>
  ) : <p className="empty">No hay datos para mostrar.</p>;
}
