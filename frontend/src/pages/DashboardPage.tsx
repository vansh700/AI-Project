import { FormEvent, useEffect, useState } from 'react';
import * as projectApi from '../api/project.api';
import type { Project } from '../types/api.types';

interface DashboardPageProps {
  onSelectProject: (projectId: string) => void;
}

export function DashboardPage({ onSelectProject }: DashboardPageProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectApi.listProjects()
      .then(setProjects)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const project = await projectApi.createProject(name, repoUrl);
      setProjects((prev) => [project, ...prev]);
      setName('');
      setRepoUrl('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    }
  }

  if (loading) return <p className="muted">Loading projects…</p>;

  return (
    <div>
      <section className="panel">
        <h2>Your Projects</h2>
        {projects.length === 0 ? (
          <p className="muted">No projects yet. Create one below.</p>
        ) : (
          <ul className="project-list">
            {projects.map((p) => (
              <li key={p.id}>
                <button type="button" className="project-item" onClick={() => onSelectProject(p.id)}>
                  <strong>{p.name}</strong>
                  <span className="muted">{p.repoUrl}</span>
                  <span className="muted">{p.storagePath ? 'Uploaded' : 'No upload'}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel">
        <h2>New Project</h2>
        <form onSubmit={handleCreate} className="inline-form">
          <input placeholder="Project name" value={name} onChange={(e) => setName(e.target.value)} required />
          <input placeholder="Repository URL" value={repoUrl} onChange={(e) => setRepoUrl(e.target.value)} required />
          <button type="submit">Create</button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>
    </div>
  );
}
