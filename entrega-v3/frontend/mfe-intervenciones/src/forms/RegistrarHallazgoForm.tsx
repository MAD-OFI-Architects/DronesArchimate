import { CommandForm } from './CommandForm';

/** Comando «Registrar hallazgo». */
export function RegistrarHallazgoForm() {
  return <CommandForm titulo="Registrar hallazgo" segmento="registrar-hallazgo" campos={[{ nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'texto', obligatorio: true }]} />;
}
