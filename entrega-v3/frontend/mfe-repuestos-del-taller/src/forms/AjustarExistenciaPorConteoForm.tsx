import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text' },
  { name: 'conteo', label: 'Conteo físico', type: 'number' },
];

export const AjustarExistenciaPorConteoForm = () => (
  <CommandForm
    titulo="Ajustar existencia por conteo"
    campos={CAMPOS}
      campoRuta="referencia"
    ruta={(r) => `/api/repuestos/existencia/${encodeURIComponent(r)}/ajustar-existencia-por-conteo`}
    camposCuerpo={['conteo']}
  />
);
