import { Router } from 'express';
import { authenticate } from '../../middlewares/jwt.middleware';
import { create, list, getById } from './project.controller';
import { uploadMiddleware, uploadRepository } from './project-upload.controller';

const router = Router();

router.use(authenticate);

router.post('/', create);
router.get('/', list);
router.get('/:id', getById);
router.post('/:id/upload', uploadMiddleware, uploadRepository);

export const projectRoutes = router;
