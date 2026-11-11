import { CommandForm } from './CommandForm';

/** Comando «Registrar ejecución de tarea». */
export function RegistrarEjecucionDeTareaForm() {
  return (
    <CommandForm
      titulo="Registrar ejecución de tarea"
      segmento="registrar-ejecucion-de-tarea"
      descripcion="Deja constancia de una tarea de mantenimiento realizada y de quién la hizo. Al registrar la primera, la orden pasa a «En ejecución»."
      identificadores={['tareaId']}
      campos={[
        { nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'texto', obligatorio: true, ayuda: 'Qué se hizo, p. ej. Cambio de hélices.' },
        { nombre: 'resultado', etiqueta: 'Resultado', tipo: 'texto', obligatorio: true, ayuda: 'Cómo terminó la tarea, p. ej. Realizada (máx. 500 caracteres).' },
        { nombre: 'ejecutadaPor', etiqueta: 'Ejecutada por', tipo: 'texto', obligatorio: true, ayuda: 'Técnico que la hizo, p. ej. Ana (máx. 100 caracteres). En trabajo mayor, esta persona no podrá firmar la liberación.' },
        { nombre: 'horas', etiqueta: 'Horas', tipo: 'numero', obligatorio: true, min: 0.25, paso: '0.25', ayuda: 'Horas-hombre dedicadas: más de 0, con pasos de cuarto de hora, p. ej. 3.5.' },
      ]}
    />
  );
}
