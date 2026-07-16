import { z } from 'zod';

export const createProjectSchema = z.object({
  name: z.string().min(1, 'Project name is required').max(100),
  repoUrl: z.string().url('Must be a valid URL'),
});

export type CreateProjectDto = z.infer<typeof createProjectSchema>;
