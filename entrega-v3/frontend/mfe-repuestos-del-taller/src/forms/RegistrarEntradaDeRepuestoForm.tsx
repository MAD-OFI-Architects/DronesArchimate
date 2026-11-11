import { CommandForm, type Campo } from './CommandForm';

const CAMPOS: Campo[] = [
  { name: 'referencia', label: 'Referencia', type: 'text', ayuda: 'Código del repuesto, p. ej. HEL-T40. Con él lo reservas, lo consultas y lo ajustas.' },
  { name: 'cantidad', label: 'Cantidad', type: 'number', min: 1, ayuda: 'Unidades que entran al almacén (entero desde 1).' },
  { name: 'stock_minimo', label: 'Stock mínimo', type: 'number', ayuda: 'Nivel de existencia a partir del cual se solicita reposición, p. ej. 2.' },
  { name: 'plazo_dias', label: 'Plazo de reposición (días)', type: 'number', ayuda: 'Días que tarda el proveedor en reponer este repuesto, p. ej. 7.' },
];

export const RegistrarEntradaDeRepuestoForm = () => (
  <CommandForm
    titulo="Registrar entrada de repuesto"
    descripcion="Registra un repuesto que entra al almacén con su existencia inicial y los niveles que activan la reposición."
    campos={CAMPOS}
    ruta={() => '/api/repuestos/existencia'}
    camposCuerpo={['referencia', 'cantidad', 'stock_minimo', 'plazo_dias']}
  />
);
