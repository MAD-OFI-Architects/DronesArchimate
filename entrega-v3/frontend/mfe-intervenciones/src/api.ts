// Cliente HTTP común del remote. Todo pasa por el gateway (/api/<servicio>/…).
export interface Problem { title?: string; detail?: string; regla?: string; codigo?: string; status?: number }
export class ApiError extends Error {
  constructor(public problem: Problem) { super(problem.detail ?? problem.title ?? 'Error'); }
}
export async function send<T = unknown>(method: 'GET' | 'POST', path: string, body?: unknown): Promise<T> {
  const res = await fetch(path, { method, headers: { 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await res.text();
  const data = text ? JSON.parse(text) : undefined;
  if (!res.ok) throw new ApiError({ ...(data ?? {}), status: res.status });
  return data as T;
}
export const notify = (message: string) => window.dispatchEvent(new CustomEvent('mfe:notify', { detail: { message } }));
