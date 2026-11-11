import { ConsultaView } from './ConsultaView';
export const ConsultaExistencia = () => <ConsultaView titulo="Consulta de existencia" etiqueta="Referencia" ruta={(id) => `/api/repuestos/existencia/${encodeURIComponent(id)}`} />;
