import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'solicitud_id', label: 'Solicitud de reposición', type: 'text' },
];

export function CancelarSolicitudForm() {
  return <CommandForm titulo="Cancelar solicitud" campos={CAMPOS} campoRuta="solicitud_id" ruta={(v) => `/api/repuestos/solicitud-de-reposicion/${encodeURIComponent(v)}/cancelar-solicitud`} camposCuerpo={[]} />;
}
