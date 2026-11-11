import { useState, type FormEvent } from 'react';
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
}
type Valor = string | boolean;

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
  campos: Campo[];
  /** Identificadores de idempotencia que el servicio exige en el cuerpo (p. ej. `tareaId`). */
  identificadores?: string[];
  sinCuerpo?: boolean;
}

/** Formulario de un comando sobre una orden de trabajo: POST /api/intervenciones/orden-de-trabajo/{id}/{segmento}. */
export function CommandForm({ titulo, segmento, campos, identificadores = [], sinCuerpo = false }: Props) {
  const [ordenId, setOrdenId] = useState('');
  const [valores, setValores] = useState<Record<string, Valor>>({});
  const [errores, setErrores] = useState<string[]>([]);
  const [fallo, setFallo] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setFallo(null);
    const invalidos = [
      ...(GUID.test(ordenId.trim()) ? [] : ['El identificador de la orden debe ser un GUID válido.']),
      ...campos.map((c) => validar(c, valores[c.nombre] ?? '')).filter((m): m is string => m !== null),
    ];
    setErrores(invalidos);
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
    <form onSubmit={onSubmit} aria-label={titulo} noValidate>
      <h3>{titulo}</h3>
      <label>Identificador de la orden<input value={ordenId} onChange={(e) => setOrdenId(e.target.value)} /></label>
      {campos.map((c) => c.tipo === 'si-no' ? (
        <label key={c.nombre} className="check">
          <input type="checkbox" checked={valores[c.nombre] === true} onChange={(e) => setValores({ ...valores, [c.nombre]: e.target.checked })} />
          {c.etiqueta}
        </label>
      ) : (
        <label key={c.nombre}>{c.etiqueta}
          <input
            type={c.tipo === 'numero' ? 'number' : c.tipo === 'fecha-hora' ? 'datetime-local' : 'text'}
            min={c.min}
            step={c.paso}
            value={String(valores[c.nombre] ?? '')}
            onChange={(e) => setValores({ ...valores, [c.nombre]: e.target.value })}
          />
        </label>
      ))}
      <button type="submit" disabled={enviando}>{titulo}</button>
      {errores.length > 0 && <ul role="alert">{errores.map((m) => <li key={m}>{m}</li>)}</ul>}
      {fallo && <p role="alert">{fallo}</p>}
    </form>
  );
}
