import path from 'path';
import fs from 'fs';
import { prisma } from '../../config/prisma.client';
import { Project } from '@prisma/client';

const STORAGE_ROOT = path.resolve(__dirname, '..', '..', '..', 'storage', 'uploads');

export async function saveUploadedFile(
  projectId: string,
  ownerId: string,
  file: Express.Multer.File
): Promise<Project> {
  const projectDir = path.join(STORAGE_ROOT, ownerId, projectId);

  // Ensure the project-scoped directory exists
  fs.mkdirSync(projectDir, { recursive: true });

  const destPath = path.join(projectDir, file.originalname);
  fs.renameSync(file.path, destPath);

  return prisma.project.update({
    where: { id: projectId },
    data: { storagePath: destPath },
  });
}
