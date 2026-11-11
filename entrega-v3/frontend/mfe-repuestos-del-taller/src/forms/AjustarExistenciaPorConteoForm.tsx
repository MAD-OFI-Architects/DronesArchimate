import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text', ayuda: 'Código del repuesto que contaste, p. ej. HEL-T40.' },
  { name: 'conteo', label: 'Conteo físico', type: 'number', ayuda: 'Unidades que hay realmente en el almacén (entero, 0 o más). La existencia se corrige a ese valor.' },
];

export const AjustarExistenciaPorConteoForm = () => (
  <CommandForm
    titulo="Ajustar existencia por conteo"
    descripcion="Corrige la existencia física de un repuesto con lo que se contó en el almacén."
    campos={CAMPOS}
      campoRuta="referencia"
    ruta={(r) => `/api/repuestos/existencia/${encodeURIComponent(r)}/ajustar-existencia-por-conteo`}
    camposCuerpo={['conteo']}
  />
);
