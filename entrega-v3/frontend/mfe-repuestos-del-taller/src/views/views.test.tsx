import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, it, expect } from 'vitest';
import { App } from '../App';
import { ConsultaExistencia } from './ConsultaExistencia';

it('consulta una existencia con GET', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, status: 200, text: async () => JSON.stringify({ referencia: 'R-1', cantidad: 4 }) })));
  render(<ConsultaExistencia />);
  await userEvent.type(screen.getByLabelText('Referencia'), 'R-1');
  await userEvent.click(screen.getByRole('button', { name: 'Consultar' }));
  expect(await screen.findByText('4')).toBeInTheDocument();
  expect((fetch as any).mock.calls[0][0]).toBe('/api/repuestos/existencia/R-1');
});

it('filtra vistas por rol', () => {
  render(<App role="Jefe de Operaciones y Mantenimiento" />);
  expect(screen.queryByLabelText('Consulta de existencia')).toBeNull();
  expect(screen.getByLabelText('Consulta de solicitud de reposición')).toBeInTheDocument();
});
