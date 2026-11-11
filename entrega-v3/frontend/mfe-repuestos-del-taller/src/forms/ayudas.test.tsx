import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { describe, expect, it } from 'vitest';
import { RegistrarEntradaDeRepuestoForm } from './RegistrarEntradaDeRepuestoForm';
import { LiberarReservaForm } from './LiberarReservaForm';
import { AjustarExistenciaPorConteoForm } from './AjustarExistenciaPorConteoForm';
import { AprobarSolicitudForm } from './AprobarSolicitudForm';
import { CancelarSolicitudForm } from './CancelarSolicitudForm';
import { ConsultaExistencia } from '../views/ConsultaExistencia';
import { ConsultaSolicitud } from '../views/ConsultaSolicitud';

const comandos: [string, ReactElement][] = [
  ['Registrar entrada de repuesto', <RegistrarEntradaDeRepuestoForm />], ['Liberar reserva', <LiberarReservaForm />],
  ['Ajustar existencia por conteo', <AjustarExistenciaPorConteoForm />], ['Aprobar solicitud', <AprobarSolicitudForm />],
  ['Cancelar solicitud', <CancelarSolicitudForm />],
];
const consultas: [string, ReactElement][] = [['Consulta de existencia', <ConsultaExistencia />], ['Consulta de solicitud', <ConsultaSolicitud />]];

function ayudasCompletas(container: HTMLElement) {
  const campos = [...container.querySelectorAll('input')];
  expect(campos.length).toBeGreaterThan(0);
  for (const campo of campos) {
    const id = campo.getAttribute('aria-describedby');
    expect(id, `sin ayuda: ${campo.outerHTML.slice(0, 80)}`).toBeTruthy();
    expect(container.querySelector(`[id="${id}"]`)?.textContent?.trim().length ?? 0).toBeGreaterThan(10);
  }
}

describe.each(comandos)('ayudas de «%s»', (_n, form) => {
  it('explica el comando y cada campo', () => {
    const { container } = render(form);
    expect(container.querySelector('h3 + p.hint')?.textContent?.length ?? 0).toBeGreaterThan(20);
    ayudasCompletas(container);
  });
});

describe.each(consultas)('ayudas de «%s»', (_n, vista) => {
  it('cada campo de búsqueda dice qué se escribe', () => ayudasCompletas(render(vista).container));
});
