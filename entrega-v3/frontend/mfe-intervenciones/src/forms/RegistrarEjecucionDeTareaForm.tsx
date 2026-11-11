import { CommandForm } from './CommandForm';

/** Comando «Registrar ejecución de tarea». */
export function RegistrarEjecucionDeTareaForm() {
  return (
    <CommandForm
      titulo="Registrar ejecución de tarea"
      segmento="registrar-ejecucion-de-tarea"
      identificadores={['tareaId']}
      campos={[
        { nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'texto', obligatorio: true },
        { nombre: 'resultado', etiqueta: 'Resultado', tipo: 'texto', obligatorio: true },
        { nombre: 'ejecutadaPor', etiqueta: 'Ejecutada por', tipo: 'texto', obligatorio: true },
        { nombre: 'horas', etiqueta: 'Horas', tipo: 'numero', obligatorio: true, min: 0, paso: '0.25' },
      ]}
    />
  );
}
