import { RegistrarEntradaDeRepuestoForm } from './forms/RegistrarEntradaDeRepuestoForm';
import { LiberarReservaForm } from './forms/LiberarReservaForm';
import { AjustarExistenciaPorConteoForm } from './forms/AjustarExistenciaPorConteoForm';
import { AprobarSolicitudForm } from './forms/AprobarSolicitudForm';
import { CancelarSolicitudForm } from './forms/CancelarSolicitudForm';
import { ConsultaExistencia } from './views/ConsultaExistencia';
import { ConsultaSolicitud } from './views/ConsultaSolicitud';

const FORMS: { roles: string[]; node: JSX.Element }[] = [
  { roles: ["Almacenista"], node: <RegistrarEntradaDeRepuestoForm key="RegistrarEntradaDeRepuestoForm" /> },
  { roles: ["Almacenista"], node: <LiberarReservaForm key="LiberarReservaForm" /> },
  { roles: ["Almacenista"], node: <AjustarExistenciaPorConteoForm key="AjustarExistenciaPorConteoForm" /> },
  { roles: ["Jefe de Operaciones y Mantenimiento"], node: <AprobarSolicitudForm key="AprobarSolicitudForm" /> },
  { roles: ["Almacenista"], node: <CancelarSolicitudForm key="CancelarSolicitudForm" /> },
  { roles: ["Almacenista"], node: <ConsultaExistencia key="ConsultaExistencia" /> },
  { roles: ["Almacenista", "Jefe de Operaciones y Mantenimiento"], node: <ConsultaSolicitud key="ConsultaSolicitud" /> },
];

/** `role` llega del shell (atributo data-role); vacío = todos los formularios de «Repuestos del Taller». */
export function App({ role }: { role: string }) {
  return (
    <main>
      <h2>Repuestos del Taller{role ? ` · ${role}` : ''}</h2>
      {FORMS.filter((f) => !role || f.roles.includes(role)).map((f) => f.node)}
    </main>
  );
}
