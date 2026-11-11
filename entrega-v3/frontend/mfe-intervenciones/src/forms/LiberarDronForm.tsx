import { CommandForm } from './CommandForm';

/** Comando «Liberar dron». */
export function LiberarDronForm() {
  return (
    <CommandForm
      titulo="Liberar dron"
      segmento="liberar-dron"
      identificadores={['liberacionId']}
      campos={[{ nombre: 'liberadaPor', etiqueta: 'Liberada por', tipo: 'texto', obligatorio: true }]}
    />
  );
}
