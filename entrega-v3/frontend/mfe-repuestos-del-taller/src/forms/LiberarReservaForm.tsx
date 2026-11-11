import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text', ayuda: 'Código del repuesto que se había reservado, p. ej. HEL-T40.' },
  { name: 'orden_trabajo_id', label: 'Orden de trabajo', type: 'text', ayuda: 'Identificador de la orden que tenía la reserva, tal como se usó al reservar.' },
];

export const LiberarReservaForm = () => (
  <CommandForm
    titulo="Liberar reserva"
    descripcion="Devuelve a disponible las unidades que una orden de trabajo tenía reservadas y no va a usar."
    campos={CAMPOS}
      campoRuta="referencia"
    ruta={(r) => `/api/repuestos/existencia/${encodeURIComponent(r)}/liberar-reserva`}
    camposCuerpo={['orden_trabajo_id']}
  />
);
