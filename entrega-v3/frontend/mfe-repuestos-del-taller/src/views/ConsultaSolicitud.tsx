import { ConsultaView } from './ConsultaView';
export const ConsultaSolicitud = () => <ConsultaView titulo="Consulta de solicitud de reposición" etiqueta="Solicitud de reposición" ayuda="Identificador de la solicitud. Las solicitudes se generan cuando una existencia llega a su stock mínimo." ruta={(id) => `/api/repuestos/solicitud-de-reposicion/${encodeURIComponent(id)}`} />;
