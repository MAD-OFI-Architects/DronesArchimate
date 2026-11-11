import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, beforeEach, it, expect } from 'vitest';
import { RegistrarEntradaDeRepuestoForm } from './RegistrarEntradaDeRepuestoForm';
import { LiberarReservaForm } from './LiberarReservaForm';
import { AjustarExistenciaPorConteoForm } from './AjustarExistenciaPorConteoForm';
import { AprobarSolicitudForm } from './AprobarSolicitudForm';
import { CancelarSolicitudForm } from './CancelarSolicitudForm';

const ok = () => ({ ok: true, status: 200, text: async () => '{}' });
beforeEach(() => { vi.stubGlobal('fetch', vi.fn(async () => ok())); });
const llamada = () => (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];

async function llenar(valores: Record<string, string>) {
  for (const [etiqueta, v] of Object.entries(valores)) await userEvent.type(screen.getByLabelText(etiqueta), v);
}

it('RegistrarEntradaDeRepuestoForm envía el cuerpo correcto', async () => {
  render(<RegistrarEntradaDeRepuestoForm />);
  await llenar({ Referencia: 'R-1', Cantidad: '5', 'Stock mínimo': '2', 'Plazo de reposición (días)': '3' });
  await userEvent.click(screen.getByRole('button', { name: 'Registrar entrada de repuesto' }));
  const [url, init] = llamada();
  expect(url).toBe('/api/repuestos/existencia');
  expect(JSON.parse(init.body)).toEqual({ referencia: 'R-1', cantidad: 5, stock_minimo: 2, plazo_dias: 3 });
});

it('RegistrarEntradaDeRepuestoForm valida campos y no envía', async () => {
  render(<RegistrarEntradaDeRepuestoForm />);
  await userEvent.click(screen.getByRole('button', { name: 'Registrar entrada de repuesto' }));
  expect(screen.getAllByRole('alert').length).toBeGreaterThan(0);
  expect(fetch).not.toHaveBeenCalled();
});

it('LiberarReservaForm envía referencia en la ruta y orden en el cuerpo', async () => {
  render(<LiberarReservaForm />);
  await llenar({ Referencia: 'R-1', 'Orden de trabajo': 'OT-9' });
  await userEvent.click(screen.getByRole('button', { name: 'Liberar reserva' }));
  const [url, init] = llamada();
  expect(url).toBe('/api/repuestos/existencia/R-1/liberar-reserva');
  expect(JSON.parse(init.body)).toEqual({ orden_trabajo_id: 'OT-9' });
});

it('AjustarExistenciaPorConteoForm envía el conteo', async () => {
  render(<AjustarExistenciaPorConteoForm />);
  await llenar({ Referencia: 'R-1', 'Conteo físico': '7' });
  await userEvent.click(screen.getByRole('button', { name: 'Ajustar existencia por conteo' }));
  const [url, init] = llamada();
  expect(url).toBe('/api/repuestos/existencia/R-1/ajustar-existencia-por-conteo');
  expect(JSON.parse(init.body)).toEqual({ conteo: 7 });
});

it('AprobarSolicitudForm envía POST sin cuerpo', async () => {
  render(<AprobarSolicitudForm />);
  await llenar({ 'Solicitud de reposición': 'abc' });
  await userEvent.click(screen.getByRole('button', { name: 'Aprobar solicitud' }));
  const [url, init] = llamada();
  expect(url).toBe('/api/repuestos/solicitud-de-reposicion/abc/aprobar-solicitud');
  expect(init.body).toBeUndefined();
});

it('CancelarSolicitudForm muestra la regla de problem+json', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => ({ ok: false, status: 409, text: async () => JSON.stringify({ regla: 'La solicitud ya fue aprobada' }) })));
  render(<CancelarSolicitudForm />);
  await llenar({ 'Solicitud de reposición': 'abc' });
  await userEvent.click(screen.getByRole('button', { name: 'Cancelar solicitud' }));
  expect(await screen.findByText('La solicitud ya fue aprobada')).toBeInTheDocument();
  expect(llamada()[0]).toBe('/api/repuestos/solicitud-de-reposicion/abc/cancelar-solicitud');
});
