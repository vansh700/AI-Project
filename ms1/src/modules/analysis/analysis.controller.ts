import { Request, Response, NextFunction } from 'express';
import { triggerAnalysis, getAnalysisJobs } from './analysis.service';

export async function startAnalysis(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const job = await triggerAnalysis(req.params.id, req.userId);
    res.status(202).json({ job });
  } catch (err) {
    next(err);
  }
}

export async function listAnalysisJobs(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const jobs = await getAnalysisJobs(req.params.id, req.userId);
    res.status(200).json({ jobs });
  } catch (err) {
    next(err);
  }
}
