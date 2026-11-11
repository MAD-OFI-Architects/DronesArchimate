import { CommandForm } from './CommandForm';

/** Comando «Asignar técnico» (agregado «Orden de trabajo»). */
export function AsignarTecnicoForm() {
  return <CommandForm titulo="Asignar técnico" segmento="asignar-tecnico" campos={[{ nombre: 'tecnico', etiqueta: 'Técnico', tipo: 'texto', obligatorio: true }]} />;
}
