import { apiFetch, setToken } from './client';

export async function register(email: string, password: string): Promise<void> {
  const data = await apiFetch<{ token: string }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.token);
}

export async function login(email: string, password: string): Promise<void> {
  const data = await apiFetch<{ token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.token);
}
