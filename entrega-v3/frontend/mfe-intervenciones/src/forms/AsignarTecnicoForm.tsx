import { CommandForm } from './CommandForm';

/** Comando «Asignar técnico» (agregado «Orden de trabajo»). */
export function AsignarTecnicoForm() {
  return (
    <CommandForm
      titulo="Asignar técnico"
      segmento="asignar-tecnico"
      descripcion="Deja a una persona como responsable de la orden. El servicio comprueba que el técnico esté habilitado antes de asignarlo."
      campos={[{ nombre: 'tecnico', etiqueta: 'Técnico', tipo: 'texto', obligatorio: true, ayuda: 'Nombre o código del técnico, p. ej. Ana. Debe estar habilitado para el trabajo.' }]}
    />
  );
}
