import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text' },
  { name: 'conteo', label: 'Conteo físico', type: 'number' },
];

export function AjustarExistenciaPorConteoForm() {
  return <CommandForm titulo="Ajustar existencia por conteo" campos={CAMPOS} campoRuta="referencia" ruta={(v) => `/api/repuestos/existencia/${encodeURIComponent(v)}/ajustar-existencia-por-conteo`} camposCuerpo={['conteo']} />;
}
