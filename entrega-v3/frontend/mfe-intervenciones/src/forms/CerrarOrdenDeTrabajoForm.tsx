import { CommandForm } from './CommandForm';

/** Comando «Cerrar orden de trabajo» (sin cuerpo). */
export function CerrarOrdenDeTrabajoForm() {
  return (
    <CommandForm
      titulo="Cerrar orden de trabajo"
      segmento="cerrar-orden-de-trabajo"
      descripcion="Cierra la orden una vez liberado el dron y publica sus consumos y horas-hombre. No necesita más datos que el identificador."
      campos={[]}
      sinCuerpo
    />
  );
}
