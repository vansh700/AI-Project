import { Router } from 'express';
import { authenticate } from '../../middlewares/jwt.middleware';
import { startAnalysis, listAnalysisJobs, getJobById, getReport } from './analysis.controller';

const router = Router({ mergeParams: true });

router.use(authenticate);

router.post('/', startAnalysis);
router.get('/', listAnalysisJobs);
router.get('/:jobId/report', getReport);
router.get('/:jobId', getJobById);

export const analysisRoutes = router;
