import { CommandForm } from './CommandForm';

/** Comando «Registrar vuelo de prueba». */
export function RegistrarVueloDePruebaForm() {
  return (
    <CommandForm
      titulo="Registrar vuelo de prueba"
      segmento="registrar-vuelo-de-prueba"
      campos={[
        { nombre: 'realizadoEn', etiqueta: 'Realizado en', tipo: 'fecha-hora', obligatorio: true },
        { nombre: 'duracionEnMinutos', etiqueta: 'Duración en minutos', tipo: 'numero', obligatorio: true, min: 1, paso: '1' },
        { nombre: 'aprobado', etiqueta: 'Aprobado', tipo: 'si-no' },
        { nombre: 'observaciones', etiqueta: 'Observaciones', tipo: 'texto', obligatorio: true },
      ]}
    />
  );
}
