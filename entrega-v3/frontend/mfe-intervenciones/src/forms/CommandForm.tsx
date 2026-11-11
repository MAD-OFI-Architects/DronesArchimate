import { useId, useState, type FormEvent } from 'react';
import { send, notify } from '../api';
import { mensajeDeError } from '../reglas';

export type TipoDeCampo = 'texto' | 'numero' | 'si-no' | 'fecha-hora';
export interface Campo {
  nombre: string;
  etiqueta: string;
  tipo: TipoDeCampo;
  obligatorio?: boolean;
  min?: number;
  paso?: string;
  /** Ayuda corta bajo el campo: qué se escribe, formato y un ejemplo. */
  ayuda?: string;
}
type Valor = string | boolean;

export const AYUDA_ID_ORDEN = 'Identificador (GUID) de la orden de trabajo, p. ej. 3f2b8c1e-5a47-4d0e-9c1b-7a6e2d4f8b90. Lo ves en la consulta de órdenes o en la respuesta al abrirla.';
const GUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const BASE = '/api/intervenciones/orden-de-trabajo';

function validar(campo: Campo, valor: Valor): string | null {
  if (campo.tipo === 'si-no') return null;
  const texto = String(valor).trim();
  if (!texto) return campo.obligatorio ? `${campo.etiqueta} es obligatorio.` : null;
  if (campo.tipo === 'numero') {
    const n = Number(texto);
    if (Number.isNaN(n)) return `${campo.etiqueta} debe ser un número.`;
    if (campo.min !== undefined && n < campo.min) return `${campo.etiqueta} debe ser al menos ${campo.min}.`;
  }
  if (campo.tipo === 'fecha-hora' && Number.isNaN(new Date(texto).getTime())) return `${campo.etiqueta} no es una fecha válida.`;
  return null;
}

function convertir(campo: Campo, valor: Valor): unknown {
  if (campo.tipo === 'si-no') return valor === true;
  const texto = String(valor).trim();
  if (!texto) return null;
  if (campo.tipo === 'numero') return Number(texto);
  if (campo.tipo === 'fecha-hora') return new Date(texto).toISOString();
  return texto;
}

interface Props {
  titulo: string;
  segmento: string;
  /** Una línea que explica para qué sirve el comando. */
  descripcion?: string;
  campos: Campo[];
  /** Identificadores de idempotencia que el servicio exige en el cuerpo (p. ej. `tareaId`). */
  identificadores?: string[];
  sinCuerpo?: boolean;
}

/** Formulario de un comando sobre una orden de trabajo: POST /api/intervenciones/orden-de-trabajo/{id}/{segmento}. */
export function CommandForm({ titulo, segmento, descripcion, campos, identificadores = [], sinCuerpo = false }: Props) {
  const uid = useId();
  const [ordenId, setOrdenId] = useState('');
  const [valores, setValores] = useState<Record<string, Valor>>({});
  const [errores, setErrores] = useState<string[]>([]);
  const [erroresPorCampo, setErroresPorCampo] = useState<Record<string, string>>({});
  const [fallo, setFallo] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setFallo(null);
    setErroresPorCampo({});
    const erroresCampos = Object.fromEntries(campos.map((c) => [c.nombre, validar(c, valores[c.nombre] ?? '')]).filter(([, error]) => error !== null)) as Record<string, string>;
    const invalidos = [
      ...(GUID.test(ordenId.trim()) ? [] : ['El identificador de la orden debe ser un GUID válido.']),
      ...Object.values(erroresCampos),
    ];
    setErrores(invalidos);
    setErroresPorCampo(erroresCampos);
    if (invalidos.length > 0) return;
    const cuerpo: Record<string, unknown> = Object.fromEntries(campos.map((c) => [c.nombre, convertir(c, valores[c.nombre] ?? '')]));
    identificadores.forEach((n) => { cuerpo[n] = crypto.randomUUID(); });
    setEnviando(true);
    try {
      await send('POST', `${BASE}/${ordenId.trim()}/${segmento}`, sinCuerpo ? undefined : cuerpo);
      notify(`${titulo}: listo`);
    } catch (err) {
      setFallo(mensajeDeError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section className="card">
      <form onSubmit={onSubmit} aria-label={titulo} noValidate>
      <h3>{titulo}</h3>
      {descripcion && <p className="hint">{descripcion}</p>}
      <div className="campo">
        <label className="field">Identificador de la orden
          <input aria-invalid={errores.some((error) => error.includes('identificador'))} aria-describedby={`${uid}-orden`} value={ordenId} onChange={(e) => setOrdenId(e.target.value)} />
        </label>
        <small className="hint" id={`${uid}-orden`}>{AYUDA_ID_ORDEN}</small>
      </div>
      {campos.map((c) => c.tipo === 'si-no' ? (
        <div className="campo" key={c.nombre}>
          <label className="field check">
            <input type="checkbox" aria-describedby={c.ayuda ? `${uid}-${c.nombre}` : undefined} checked={valores[c.nombre] === true} onChange={(e) => setValores({ ...valores, [c.nombre]: e.target.checked })} />
            {c.etiqueta}
          </label>
          {c.ayuda && <small className="hint" id={`${uid}-${c.nombre}`}>{c.ayuda}</small>}
        </div>
      ) : (
        <div className="campo" key={c.nombre}>
          <label className="field">{c.etiqueta}
            <input
              aria-invalid={Boolean(erroresPorCampo[c.nombre])}
              aria-describedby={c.ayuda ? `${uid}-${c.nombre}` : undefined}
              type={c.tipo === 'numero' ? 'number' : c.tipo === 'fecha-hora' ? 'datetime-local' : 'text'}
              min={c.min}
              step={c.paso}
              value={String(valores[c.nombre] ?? '')}
              onChange={(e) => setValores({ ...valores, [c.nombre]: e.target.value })}
            />
          </label>
          {c.ayuda && <small className="hint" id={`${uid}-${c.nombre}`}>{c.ayuda}</small>}
        </div>
      ))}
      <button type="submit" disabled={enviando}>{enviando ? 'Enviando…' : titulo}</button>
      {errores.length > 0 && <ul role="alert">{errores.map((m) => <li key={m}>{m}</li>)}</ul>}
      {fallo && <p role="alert">{fallo}</p>}
      </form>
    </section>
  );
}
