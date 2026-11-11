import { ConsultaView } from './ConsultaView';
export const ConsultaExistencia = () => <ConsultaView titulo="Consulta de existencia" etiqueta="Referencia" ayuda="Código del repuesto, p. ej. HEL-T40. Muestra la existencia física, lo reservado y lo disponible." ruta={(id) => `/api/repuestos/existencia/${encodeURIComponent(id)}`} />;
