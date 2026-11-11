import { CommandForm } from './CommandForm';

/** Comando «Registrar consumo de repuesto». */
export function RegistrarConsumoDeRepuestoForm() {
  return (
    <CommandForm
      titulo="Registrar consumo de repuesto"
      segmento="registrar-consumo-de-repuesto"
      descripcion="Anota un repuesto usado en la orden. Si el repuesto se controla por serie, indica cuál se retiró y cuál se instaló."
      identificadores={['consumoId']}
      campos={[
        { nombre: 'referencia', etiqueta: 'Referencia', tipo: 'texto', obligatorio: true, ayuda: 'Código del repuesto, p. ej. HEL-T40 (máx. 100 caracteres).' },
        { nombre: 'cantidad', etiqueta: 'Cantidad', tipo: 'numero', obligatorio: true, min: 1, paso: '1', ayuda: 'Unidades consumidas (entero desde 1).' },
        { nombre: 'requiereSerie', etiqueta: 'Requiere serie', tipo: 'si-no', ayuda: 'Márcalo si este repuesto se controla por número de serie.' },
        { nombre: 'serieRetirada', etiqueta: 'Serie retirada', tipo: 'texto', ayuda: 'Serie de la pieza que se quitó del dron, si aplica (máx. 100 caracteres).' },
        { nombre: 'serieInstalada', etiqueta: 'Serie instalada', tipo: 'texto', ayuda: 'Serie de la pieza nueva (máx. 100 caracteres). Es obligatoria si marcaste «Requiere serie».' },
        { nombre: 'horaDeCorte', etiqueta: 'Hora de corte', tipo: 'numero', min: 0, ayuda: 'Horas acumuladas del componente en el momento del cambio (0 o más). Queda en la orden y el contador de la pieza nueva arranca en cero.' },
      ]}
    />
  );
}
