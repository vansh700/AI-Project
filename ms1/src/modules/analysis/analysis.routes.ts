import { Router } from 'express';
import { authenticate } from '../../middlewares/jwt.middleware';
import { startAnalysis, listAnalysisJobs } from './analysis.controller';

const router = Router({ mergeParams: true });

router.use(authenticate);

router.post('/', startAnalysis);
router.get('/', listAnalysisJobs);

export const analysisRoutes = router;
