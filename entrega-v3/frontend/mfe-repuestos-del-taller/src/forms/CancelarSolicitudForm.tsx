import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [{ name: 'solicitud_id', label: 'Solicitud de reposición', type: 'text', ayuda: 'Identificador de la solicitud, el que ves al consultar solicitudes de reposición.' }];

export const CancelarSolicitudForm = () => (
  <CommandForm
    titulo="Cancelar solicitud"
    descripcion="Cancela una solicitud de reposición que ya no se necesita."
    campos={CAMPOS}
      campoRuta="solicitud_id"
    ruta={(id) => `/api/repuestos/solicitud-de-reposicion/${encodeURIComponent(id)}/cancelar-solicitud`}
    camposCuerpo={[]}
  />
);
