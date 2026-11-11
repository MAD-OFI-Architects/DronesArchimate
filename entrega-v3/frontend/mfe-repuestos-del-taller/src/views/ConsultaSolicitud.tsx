import { ConsultaView } from './ConsultaView';
export const ConsultaSolicitud = () => <ConsultaView titulo="Consulta de solicitud de reposición" etiqueta="Solicitud de reposición" ruta={(id) => `/api/repuestos/solicitud-de-reposicion/${encodeURIComponent(id)}`} />;
