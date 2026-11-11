import { useId, useState, type FormEvent } from 'react';
import { send, notify, mensajeDeError } from '../api';

/** `ayuda`: texto corto bajo el campo (qué se escribe, formato y un ejemplo). */
export interface Campo { name: string; label: string; type: 'text' | 'number'; min?: number; ayuda?: string }
export interface CommandFormProps {
  titulo: string;
  /** Una línea que explica para qué sirve el comando. */
  descripcion?: string;
  campos: Campo[];
  /** Campo que viaja en la ruta (no en el cuerpo); ausente si la ruta es fija. */
  campoRuta?: string;
  ruta: (valor: string) => string;
  /** Campos que viajan en el cuerpo; vacío = sin cuerpo. */
  camposCuerpo: string[];
}

export function CommandForm({ titulo, descripcion, campos, campoRuta, ruta, camposCuerpo }: CommandFormProps) {
  const uid = useId();
  const [valores, setValores] = useState<Record<string, string>>({});
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  function validar(): Record<string, string> {
    const faltan: Record<string, string> = {};
    for (const c of campos) {
      const v = (valores[c.name] ?? '').trim();
      if (!v) faltan[c.name] = `${c.label} es obligatorio`;
      else if (c.type === 'number' && (!Number.isInteger(Number(v)) || Number(v) < (c.min ?? 0))) faltan[c.name] = `${c.label} debe ser un entero mayor o igual a ${c.min ?? 0}`;
    }
    return faltan;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const faltan = validar();
    setErrores(faltan);
    if (Object.keys(faltan).length) return;
    const cuerpo = Object.fromEntries(camposCuerpo.map((n) => {
      const c = campos.find((x) => x.name === n)!;
      return [n, c.type === 'number' ? Number(valores[n]) : valores[n].trim()];
    }));
    try {
      setEnviando(true);
      await send('POST', ruta(campoRuta ? valores[campoRuta].trim() : ''), camposCuerpo.length ? cuerpo : undefined);
      notify(`${titulo}: listo`);
    } catch (err) {
      setError(mensajeDeError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section className="card">
      <form onSubmit={onSubmit} aria-label={titulo} noValidate>
        <h3>{titulo}</h3>
        {descripcion && <p className="hint">{descripcion}</p>}
      {campos.map((c) => (
        <div className="campo" key={c.name}>
          <label className="field">{c.label}
            <input type={c.type} min={c.min} value={valores[c.name] ?? ''} aria-invalid={!!errores[c.name]}
              aria-describedby={c.ayuda ? `${uid}-${c.name}` : undefined}
              onChange={(e) => setValores({ ...valores, [c.name]: e.target.value })} />
            {errores[c.name] && <span role="alert">{errores[c.name]}</span>}
          </label>
          {c.ayuda && <small className="hint" id={`${uid}-${c.name}`}>{c.ayuda}</small>}
        </div>
      ))}
        <button className="btn" type="submit" disabled={enviando}>{enviando ? 'Enviando…' : titulo}</button>
        {error && <p role="alert" className="alert">{error}</p>}
      </form>
    </section>
  );
}
