import { Request, Response, NextFunction } from 'express';
import { createProjectSchema } from './project.validation';
import { createNewProject, getProjectsForUser, getProjectDetail } from './project.service';

export async function create(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const dto = createProjectSchema.parse(req.body);
    const project = await createNewProject(dto, req.userId);
    res.status(201).json({ project });
  } catch (err) {
    next(err);
  }
}

export async function list(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const projects = await getProjectsForUser(req.userId);
    res.status(200).json({ projects });
  } catch (err) {
    next(err);
  }
}

export async function getById(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const project = await getProjectDetail(req.params.id, req.userId);
    res.status(200).json({ project });
  } catch (err) {
    next(err);
  }
}
