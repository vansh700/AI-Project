import { apiFetch } from './client';
import type { Project } from '../types/api.types';

export async function listProjects(): Promise<Project[]> {
  const data = await apiFetch<{ projects: Project[] }>('/projects');
  return data.projects;
}

export async function createProject(name: string, repoUrl: string): Promise<Project> {
  const data = await apiFetch<{ project: Project }>('/projects', {
    method: 'POST',
    body: JSON.stringify({ name, repoUrl }),
  });
  return data.project;
}

export async function getProject(id: string): Promise<Project> {
  const data = await apiFetch<{ project: Project }>(`/projects/${id}`);
  return data.project;
}

export async function uploadRepository(projectId: string, file: File): Promise<Project> {
  const form = new FormData();
  form.append('file', file);

  const data = await apiFetch<{ project: Project }>(`/projects/${projectId}/upload`, {
    method: 'POST',
    body: form,
  });
  return data.project;
}
