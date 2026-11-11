import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text' },
  { name: 'orden_trabajo_id', label: 'Orden de trabajo', type: 'text' },
];

export const LiberarReservaForm = () => (
  <CommandForm
    titulo="Liberar reserva"
    campos={CAMPOS}
      campoRuta="referencia"
    ruta={(r) => `/api/repuestos/existencia/${encodeURIComponent(r)}/liberar-reserva`}
    camposCuerpo={['orden_trabajo_id']}
  />
);
