import { Project } from '@prisma/client';
import { CreateProjectDto } from './project.validation';
import { createProject, findProjectsByOwner, findProjectById } from './project.repository';

export async function createNewProject(dto: CreateProjectDto, ownerId: string): Promise<Project> {
  return createProject({ name: dto.name, repoUrl: dto.repoUrl, ownerId });
}

export async function getProjectsForUser(ownerId: string): Promise<Project[]> {
  return findProjectsByOwner(ownerId);
}

export async function getProjectDetail(projectId: string, ownerId: string): Promise<Project> {
  const project = await findProjectById(projectId);

  if (!project) {
    throw Object.assign(new Error('Project not found'), { statusCode: 404 });
  }

  // Users can only view their own projects
  if (project.ownerId !== ownerId) {
    throw Object.assign(new Error('Project not found'), { statusCode: 404 });
  }

  return project;
}
