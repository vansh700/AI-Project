import { Router } from 'express';
import { handleJobComplete } from './webhook.controller';

const router = Router();

// Internal-only route — secret verification is done inside the controller
router.post('/job-complete', handleJobComplete);

export const webhookRoutes = router;
