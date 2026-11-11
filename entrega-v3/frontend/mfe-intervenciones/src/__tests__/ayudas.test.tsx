import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { describe, expect, it } from 'vitest';
import { AsignarTecnicoForm } from '../forms/AsignarTecnicoForm';
import { RegistrarEjecucionDeTareaForm } from '../forms/RegistrarEjecucionDeTareaForm';
import { RegistrarConsumoDeRepuestoForm } from '../forms/RegistrarConsumoDeRepuestoForm';
import { RegistrarHallazgoForm } from '../forms/RegistrarHallazgoForm';
import { RegistrarVueloDePruebaForm } from '../forms/RegistrarVueloDePruebaForm';
import { LiberarDronForm } from '../forms/LiberarDronForm';
import { CerrarOrdenDeTrabajoForm } from '../forms/CerrarOrdenDeTrabajoForm';
import { OrdenDeTrabajoConsulta } from '../views/OrdenDeTrabajoConsulta';

const formularios: [string, ReactElement][] = [
  ['Asignar técnico', <AsignarTecnicoForm />], ['Registrar ejecución de tarea', <RegistrarEjecucionDeTareaForm />],
  ['Registrar consumo de repuesto', <RegistrarConsumoDeRepuestoForm />], ['Registrar hallazgo', <RegistrarHallazgoForm />],
  ['Registrar vuelo de prueba', <RegistrarVueloDePruebaForm />], ['Liberar dron', <LiberarDronForm />],
  ['Cerrar orden de trabajo', <CerrarOrdenDeTrabajoForm />],
];

describe.each(formularios)('ayudas de «%s»', (_nombre, form) => {
  it('explica para qué sirve el comando', () => {
    const { container } = render(form);
    const descripcion = container.querySelector('h3 + p.hint');
    expect(descripcion?.textContent?.length ?? 0).toBeGreaterThan(20);
  });

  it('cada campo tiene una ayuda enlazada con aria-describedby', () => {
    const { container } = render(form);
    const campos = [...container.querySelectorAll('input')];
    expect(campos.length).toBeGreaterThan(0);
    for (const campo of campos) {
      const id = campo.getAttribute('aria-describedby');
      expect(id, `sin ayuda: ${campo.outerHTML.slice(0, 80)}`).toBeTruthy();
      expect(container.querySelector(`[id="${id}"]`)?.textContent?.trim().length ?? 0).toBeGreaterThan(10);
    }
  });
});

describe('ayudas de la consulta', () => {
  it('el identificador de la orden dice qué es y de dónde sale', () => {
    const { container } = render(<OrdenDeTrabajoConsulta />);
    const ayuda = container.querySelector('#ayuda-consulta-orden');
    expect(ayuda?.textContent).toContain('GUID');
    expect(container.querySelector('input')?.getAttribute('aria-describedby')).toBe('ayuda-consulta-orden');
  });
});
