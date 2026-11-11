import { CommandForm } from './CommandForm';

/** Comando «Registrar consumo de repuesto». */
export function RegistrarConsumoDeRepuestoForm() {
  return (
    <CommandForm
      titulo="Registrar consumo de repuesto"
      segmento="registrar-consumo-de-repuesto"
      identificadores={['consumoId']}
      campos={[
        { nombre: 'referencia', etiqueta: 'Referencia', tipo: 'texto', obligatorio: true },
        { nombre: 'cantidad', etiqueta: 'Cantidad', tipo: 'numero', obligatorio: true, min: 1, paso: '1' },
        { nombre: 'requiereSerie', etiqueta: 'Requiere serie', tipo: 'si-no' },
        { nombre: 'serieRetirada', etiqueta: 'Serie retirada', tipo: 'texto' },
        { nombre: 'serieInstalada', etiqueta: 'Serie instalada', tipo: 'texto' },
        { nombre: 'horaDeCorte', etiqueta: 'Hora de corte', tipo: 'numero', min: 0 },
      ]}
    />
  );
}
