import { useState, type FormEvent } from 'react';
import { send, notify, mensajeDeError } from '../api';

export interface Campo { name: string; label: string; type: 'text' | 'number'; min?: number }
export interface CommandFormProps {
  titulo: string;
  campos: Campo[];
  /** Campo que viaja en la ruta (no en el cuerpo). */
  campoRuta: string;
  ruta: (valor: string) => string;
  /** Campos que viajan en el cuerpo; vacío = sin cuerpo. */
  camposCuerpo: string[];
}

export function CommandForm({ titulo, campos, campoRuta, ruta, camposCuerpo }: CommandFormProps) {
  const [valores, setValores] = useState<Record<string, string>>({});
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

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
      await send('POST', ruta(valores[campoRuta].trim()), camposCuerpo.length ? cuerpo : undefined);
      notify(`${titulo}: listo`);
    } catch (err) {
      setError(mensajeDeError(err));
    }
  }

  return (
    <form onSubmit={onSubmit} aria-label={titulo} noValidate>
      <h3>{titulo}</h3>
      {campos.map((c) => (
        <label key={c.name}>{c.label}
          <input type={c.type} min={c.min} value={valores[c.name] ?? ''} aria-invalid={!!errores[c.name]}
            onChange={(e) => setValores({ ...valores, [c.name]: e.target.value })} />
          {errores[c.name] && <span role="alert">{errores[c.name]}</span>}
        </label>
      ))}
      <button type="submit">{titulo}</button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
