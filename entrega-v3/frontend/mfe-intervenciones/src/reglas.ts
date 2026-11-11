import { ApiError } from './api';

const MENSAJES: Record<string, string> = {
  ORDEN_CERRADA_INMUTABLE: 'La orden de trabajo ya está cerrada y no admite cambios.',
  PARADA_INEXISTENTE: 'La parada programada de la orden no existe.',
  SERIE_FALTANTE: 'Falta la serie instalada de un repuesto que la exige.',
  LIBERA_EL_MISMO_QUE_EJECUTO: 'La liberación debe hacerla una persona distinta de quien ejecutó el trabajo.',
  PRUEBA_DE_VUELO_PENDIENTE: 'En trabajos mayores la liberación exige un vuelo de prueba aprobado.',
  TECNICO_NO_HABILITADO: 'El técnico no tiene una habilitación vigente.',
};

/** Texto en lenguaje claro para un error de la API (problem+json con campos `codigo` y `regla`). */
export function mensajeDeError(err: unknown): string {
  if (!(err instanceof ApiError)) return 'No se pudo completar la operación. Inténtelo de nuevo.';
  const { regla, codigo, detail, title, status } = err.problem;
  if (codigo && MENSAJES[codigo]) return MENSAJES[codigo];
  if (regla) return MENSAJES[regla] ?? `Regla de negocio incumplida: ${regla}.`;
  return detail ?? title ?? `La operación fue rechazada (${status ?? 'error'}).`;
}
