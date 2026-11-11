import { AsignarTecnicoForm } from './forms/AsignarTecnicoForm';
import { RegistrarEjecucionDeTareaForm } from './forms/RegistrarEjecucionDeTareaForm';
import { RegistrarConsumoDeRepuestoForm } from './forms/RegistrarConsumoDeRepuestoForm';
import { RegistrarHallazgoForm } from './forms/RegistrarHallazgoForm';
import { RegistrarVueloDePruebaForm } from './forms/RegistrarVueloDePruebaForm';
import { LiberarDronForm } from './forms/LiberarDronForm';
import { CerrarOrdenDeTrabajoForm } from './forms/CerrarOrdenDeTrabajoForm';
import { OrdenDeTrabajoConsulta } from './views/OrdenDeTrabajoConsulta';

const FORMS: { roles: string[]; node: JSX.Element }[] = [
  { roles: ["Jefe de Operaciones y Mantenimiento"], node: <AsignarTecnicoForm key="AsignarTecnicoForm" /> },
  { roles: ["Técnico de mantenimiento"], node: <RegistrarEjecucionDeTareaForm key="RegistrarEjecucionDeTareaForm" /> },
  { roles: ["Técnico de mantenimiento"], node: <RegistrarConsumoDeRepuestoForm key="RegistrarConsumoDeRepuestoForm" /> },
  { roles: ["Técnico de mantenimiento"], node: <RegistrarHallazgoForm key="RegistrarHallazgoForm" /> },
  { roles: ["Técnico de mantenimiento"], node: <RegistrarVueloDePruebaForm key="RegistrarVueloDePruebaForm" /> },
  { roles: ["Jefe de Operaciones y Mantenimiento"], node: <LiberarDronForm key="LiberarDronForm" /> },
  { roles: ["Técnico de mantenimiento"], node: <CerrarOrdenDeTrabajoForm key="CerrarOrdenDeTrabajoForm" /> },
];

/** `role` llega del shell (atributo data-role); vacío = todos los formularios de «Intervenciones». */
export function App({ role }: { role: string }) {
  return (
    <main>
      <h2>Intervenciones{role ? ` · ${role}` : ''}</h2>
      <OrdenDeTrabajoConsulta />
      {FORMS.filter((f) => !role || f.roles.includes(role)).map((f) => f.node)}
    </main>
  );
}
