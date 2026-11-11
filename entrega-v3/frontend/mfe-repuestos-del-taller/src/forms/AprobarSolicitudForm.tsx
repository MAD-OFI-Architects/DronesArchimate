import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'solicitud_id', label: 'Solicitud de reposición', type: 'text' },
];

export function AprobarSolicitudForm() {
  return <CommandForm titulo="Aprobar solicitud" campos={CAMPOS} campoRuta="solicitud_id" ruta={(v) => `/api/repuestos/solicitud-de-reposicion/${encodeURIComponent(v)}/aprobar-solicitud`} camposCuerpo={[]} />;
}
