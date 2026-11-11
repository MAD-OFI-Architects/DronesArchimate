import { CommandForm } from './CommandForm';

/** Comando «Registrar vuelo de prueba». */
export function RegistrarVueloDePruebaForm() {
  return (
    <CommandForm
      titulo="Registrar vuelo de prueba"
      segmento="registrar-vuelo-de-prueba"
      descripcion="Registra el vuelo con el que se comprueba el dron tras la intervención. Un trabajo mayor no se libera sin un vuelo aprobado."
      campos={[
        { nombre: 'realizadoEn', etiqueta: 'Realizado en', tipo: 'fecha-hora', obligatorio: true, ayuda: 'Fecha y hora en que se hizo el vuelo.' },
        { nombre: 'duracionEnMinutos', etiqueta: 'Duración en minutos', tipo: 'numero', obligatorio: true, min: 1, paso: '1', ayuda: 'Minutos de vuelo (entero desde 1), p. ej. 8.' },
        { nombre: 'aprobado', etiqueta: 'Aprobado', tipo: 'si-no', ayuda: 'Márcalo si el dron superó la prueba.' },
        { nombre: 'observaciones', etiqueta: 'Observaciones', tipo: 'texto', obligatorio: true, ayuda: 'Lo que notaste durante el vuelo, p. ej. Sin novedades.' },
      ]}
    />
  );
}
