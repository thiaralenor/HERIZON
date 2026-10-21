const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const errorBody = await response.json().catch(() => null) as { detail?: unknown } | null;
    const detail = typeof errorBody?.detail === 'string' ? errorBody.detail : null;
    throw new Error(detail ?? `API request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}
