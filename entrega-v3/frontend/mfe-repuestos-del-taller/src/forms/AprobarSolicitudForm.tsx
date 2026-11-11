import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [{ name: 'solicitud_id', label: 'Solicitud de reposición', type: 'text', ayuda: 'Identificador de la solicitud, el que ves al consultar solicitudes de reposición.' }];

export const AprobarSolicitudForm = () => (
  <CommandForm
    titulo="Aprobar solicitud"
    descripcion="Aprueba una solicitud de reposición para que se pida al proveedor."
    campos={CAMPOS}
      campoRuta="solicitud_id"
    ruta={(id) => `/api/repuestos/solicitud-de-reposicion/${encodeURIComponent(id)}/aprobar-solicitud`}
    camposCuerpo={[]}
  />
);
