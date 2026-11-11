import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text' },
  { name: 'orden_trabajo_id', label: 'Orden de trabajo', type: 'text' },
];

export function LiberarReservaForm() {
  return <CommandForm titulo="Liberar reserva" campos={CAMPOS} campoRuta="referencia" ruta={(v) => `/api/repuestos/existencia/${encodeURIComponent(v)}/liberar-reserva`} camposCuerpo={['orden_trabajo_id']} />;
}
