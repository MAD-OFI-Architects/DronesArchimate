import { CommandForm } from './CommandForm';

/** Comando «Cerrar orden de trabajo» (sin cuerpo). */
export function CerrarOrdenDeTrabajoForm() {
  return <CommandForm titulo="Cerrar orden de trabajo" segmento="cerrar-orden-de-trabajo" campos={[]} sinCuerpo />;
}
