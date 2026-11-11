import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactElement } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AsignarTecnicoForm } from '../forms/AsignarTecnicoForm';
import { RegistrarEjecucionDeTareaForm } from '../forms/RegistrarEjecucionDeTareaForm';
import { RegistrarConsumoDeRepuestoForm } from '../forms/RegistrarConsumoDeRepuestoForm';
import { RegistrarHallazgoForm } from '../forms/RegistrarHallazgoForm';
import { RegistrarVueloDePruebaForm } from '../forms/RegistrarVueloDePruebaForm';
import { LiberarDronForm } from '../forms/LiberarDronForm';
import { CerrarOrdenDeTrabajoForm } from '../forms/CerrarOrdenDeTrabajoForm';
import { OrdenDeTrabajoConsulta } from '../views/OrdenDeTrabajoConsulta';
import { App } from '../App';

const ORDEN = '11111111-1111-4111-8111-111111111111';
const UUID = '22222222-2222-4222-8222-222222222222';
const BASE = `/api/intervenciones/orden-de-trabajo/${ORDEN}`;

const respuesta = (status: number, cuerpo?: unknown) =>
  Promise.resolve(new Response(cuerpo === undefined ? null : JSON.stringify(cuerpo), { status }));

let fetchSimulado: ReturnType<typeof vi.fn>;
beforeEach(() => {
  fetchSimulado = vi.fn(() => respuesta(204));
  vi.stubGlobal('fetch', fetchSimulado);
  vi.spyOn(crypto, 'randomUUID').mockReturnValue(UUID);
});
afterEach(() => vi.restoreAllMocks());

const escribir = async (etiqueta: string, texto: string) => userEvent.type(screen.getByLabelText(etiqueta), texto);
const enviadoA = () => fetchSimulado.mock.calls[0] as [string, RequestInit];

interface Caso { nombre: string; form: ReactElement; titulo: string; segmento: string; rellenar: () => Promise<void>; cuerpo?: unknown }
const casos: Caso[] = [
  { nombre: 'AsignarTecnicoForm', form: <AsignarTecnicoForm />, titulo: 'Asignar técnico', segmento: 'asignar-tecnico',
    rellenar: async () => escribir('Técnico', 'Ana'), cuerpo: { tecnico: 'Ana' } },
  { nombre: 'RegistrarEjecucionDeTareaForm', form: <RegistrarEjecucionDeTareaForm />, titulo: 'Registrar ejecución de tarea', segmento: 'registrar-ejecucion-de-tarea',
    rellenar: async () => { await escribir('Descripción', 'Cambiar hélice'); await escribir('Resultado', 'OK'); await escribir('Ejecutada por', 'Ana'); await escribir('Horas', '2.5'); },
    cuerpo: { descripcion: 'Cambiar hélice', resultado: 'OK', ejecutadaPor: 'Ana', horas: 2.5, tareaId: UUID } },
  { nombre: 'RegistrarConsumoDeRepuestoForm', form: <RegistrarConsumoDeRepuestoForm />, titulo: 'Registrar consumo de repuesto', segmento: 'registrar-consumo-de-repuesto',
    rellenar: async () => { await escribir('Referencia', 'HEL-01'); await escribir('Cantidad', '2'); await userEvent.click(screen.getByLabelText('Requiere serie')); await escribir('Serie instalada', 'S-9'); },
    cuerpo: { referencia: 'HEL-01', cantidad: 2, requiereSerie: true, serieRetirada: null, serieInstalada: 'S-9', horaDeCorte: null, consumoId: UUID } },
  { nombre: 'RegistrarHallazgoForm', form: <RegistrarHallazgoForm />, titulo: 'Registrar hallazgo', segmento: 'registrar-hallazgo',
    rellenar: async () => escribir('Descripción', 'Fisura'), cuerpo: { descripcion: 'Fisura' } },
  { nombre: 'RegistrarVueloDePruebaForm', form: <RegistrarVueloDePruebaForm />, titulo: 'Registrar vuelo de prueba', segmento: 'registrar-vuelo-de-prueba',
    rellenar: async () => { await escribir('Realizado en', '2026-05-01T10:30'); await escribir('Duración en minutos', '15'); await userEvent.click(screen.getByLabelText('Aprobado')); await escribir('Observaciones', 'Sin novedad'); },
    cuerpo: { realizadoEn: new Date('2026-05-01T10:30').toISOString(), duracionEnMinutos: 15, aprobado: true, observaciones: 'Sin novedad' } },
  { nombre: 'LiberarDronForm', form: <LiberarDronForm />, titulo: 'Liberar dron', segmento: 'liberar-dron',
    rellenar: async () => escribir('Liberada por', 'Luis'), cuerpo: { liberadaPor: 'Luis', liberacionId: UUID } },
  { nombre: 'CerrarOrdenDeTrabajoForm', form: <CerrarOrdenDeTrabajoForm />, titulo: 'Cerrar orden de trabajo', segmento: 'cerrar-orden-de-trabajo',
    rellenar: async () => undefined },
];

describe.each(casos)('$nombre', (c) => {
  it('envía el cuerpo correcto a la ruta del comando', async () => {
    render(c.form);
    await escribir('Identificador de la orden', ORDEN);
    await c.rellenar();
    await userEvent.click(screen.getByRole('button', { name: c.titulo }));
    const [url, init] = enviadoA();
    expect(url).toBe(`${BASE}/${c.segmento}`);
    expect(init.method).toBe('POST');
    if (c.cuerpo === undefined) expect(init.body).toBeUndefined();
    else expect(JSON.parse(init.body as string)).toEqual(c.cuerpo);
  });

  it('valida el identificador de la orden y no envía', async () => {
    render(c.form);
    await userEvent.click(screen.getByRole('button', { name: c.titulo }));
    expect(screen.getByRole('alert')).toHaveTextContent('GUID válido');
    expect(fetchSimulado).not.toHaveBeenCalled();
  });

  it('muestra la regla de problem+json en lenguaje claro', async () => {
    fetchSimulado.mockImplementation(() => respuesta(422, { title: 'Regla', regla: 'ORDEN_CERRADA_INMUTABLE' }));
    render(c.form);
    await escribir('Identificador de la orden', ORDEN);
    await c.rellenar();
    await userEvent.click(screen.getByRole('button', { name: c.titulo }));
    expect(await screen.findByText(/ya está cerrada/)).toBeInTheDocument();
  });
});

describe('validación de campos', () => {
  it('exige campos obligatorios', async () => {
    render(<AsignarTecnicoForm />);
    await escribir('Identificador de la orden', ORDEN);
    await userEvent.click(screen.getByRole('button', { name: 'Asignar técnico' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Técnico es obligatorio');
    expect(fetchSimulado).not.toHaveBeenCalled();
  });

  it('rechaza una cantidad menor que 1', async () => {
    render(<RegistrarConsumoDeRepuestoForm />);
    await escribir('Identificador de la orden', ORDEN);
    await escribir('Referencia', 'X');
    await escribir('Cantidad', '0');
    await userEvent.click(screen.getByRole('button', { name: 'Registrar consumo de repuesto' }));
    expect(screen.getByRole('alert')).toHaveTextContent('al menos 1');
    expect(fetchSimulado).not.toHaveBeenCalled();
  });
});

describe('OrdenDeTrabajoConsulta', () => {
  it('consulta con GET y muestra el detalle', async () => {
    fetchSimulado.mockImplementation(() => respuesta(200, { id: ORDEN, dronId: 'D-1', tipo: 'Preventiva', estado: 'EnEjecucion', tecnico: 'Ana', horasHombre: 3, tareas: [], consumos: [], hallazgos: [] }));
    render(<OrdenDeTrabajoConsulta />);
    await escribir('Identificador de la orden', ORDEN);
    await userEvent.click(screen.getByRole('button', { name: 'Consultar' }));
    expect(await screen.findByText('EnEjecucion')).toBeInTheDocument();
    expect(enviadoA()[0]).toBe(BASE);
    expect(enviadoA()[1].method).toBe('GET');
  });
});

describe('App', () => {
  it('filtra los formularios por rol', () => {
    render(<App role="Técnico de mantenimiento" />);
    expect(screen.getByRole('form', { name: 'Registrar hallazgo' })).toBeInTheDocument();
    expect(screen.queryByRole('form', { name: 'Asignar técnico' })).not.toBeInTheDocument();
    expect(screen.getByRole('form', { name: 'Consultar orden de trabajo' })).toBeInTheDocument();
  });
});
