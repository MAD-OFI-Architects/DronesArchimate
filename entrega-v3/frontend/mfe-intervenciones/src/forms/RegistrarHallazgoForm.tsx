import { CommandForm } from './CommandForm';

/** Comando «Registrar hallazgo». */
export function RegistrarHallazgoForm() {
  return (
    <CommandForm
      titulo="Registrar hallazgo"
      segmento="registrar-hallazgo"
      descripcion="Anota algo anormal que se encontró durante la inspección o la reparación."
      campos={[{ nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'texto', obligatorio: true, ayuda: 'Qué se observó, p. ej. Desgaste leve en el soporte del motor.' }]}
    />
  );
}
