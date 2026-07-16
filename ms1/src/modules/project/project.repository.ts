import { Project } from '@prisma/client';
import { prisma } from '../../config/prisma.client';

export async function createProject(data: { name: string; repoUrl: string; ownerId: string }): Promise<Project> {
  return prisma.project.create({ data });
}

export async function findProjectsByOwner(ownerId: string): Promise<Project[]> {
  return prisma.project.findMany({ where: { ownerId }, orderBy: { createdAt: 'desc' } });
}

export async function findProjectById(id: string): Promise<Project | null> {
  return prisma.project.findUnique({ where: { id } });
}
