import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text' },
  { name: 'cantidad', label: 'Cantidad', type: 'number', min: 1 },
  { name: 'stock_minimo', label: 'Stock mínimo', type: 'number' },
  { name: 'plazo_dias', label: 'Plazo de reposición (días)', type: 'number', min: 1 },
];

export function RegistrarEntradaDeRepuestoForm() {
  return <CommandForm titulo="Registrar entrada de repuesto" campos={CAMPOS} campoRuta="referencia" ruta={() => "/api/repuestos/existencia"} camposCuerpo={['referencia', 'cantidad', 'stock_minimo', 'plazo_dias']} />;
}
