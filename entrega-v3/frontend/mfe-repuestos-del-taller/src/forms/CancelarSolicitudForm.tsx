import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [{ name: 'solicitud_id', label: 'Solicitud de reposición', type: 'text' }];

export const CancelarSolicitudForm = () => (
  <CommandForm
    titulo="Cancelar solicitud"
    campos={CAMPOS}
      campoRuta="solicitud_id"
    ruta={(id) => `/api/repuestos/solicitud-de-reposicion/${encodeURIComponent(id)}/cancelar-solicitud`}
    camposCuerpo={[]}
  />
);
