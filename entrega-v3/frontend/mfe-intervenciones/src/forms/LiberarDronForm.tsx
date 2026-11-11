import { CommandForm } from './CommandForm';

/** Comando «Liberar dron». */
export function LiberarDronForm() {
  return (
    <CommandForm
      titulo="Liberar dron"
      segmento="liberar-dron"
      descripcion="Firma que el dron queda listo para operar. En un trabajo mayor exige un vuelo de prueba aprobado y que firme alguien distinto de quien ejecutó las tareas."
      identificadores={['liberacionId']}
      campos={[{ nombre: 'liberadaPor', etiqueta: 'Liberada por', tipo: 'texto', obligatorio: true, ayuda: 'Nombre de quien firma la liberación, p. ej. Beto (máx. 100 caracteres). En trabajo mayor no puede ser quien ejecutó una tarea.' }]}
    />
  );
}
