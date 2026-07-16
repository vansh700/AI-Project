import multer from 'multer';
import path from 'path';
import os from 'os';
import { Request, Response, NextFunction } from 'express';
import { getProjectDetail } from './project.service';
import { saveUploadedFile } from './project-upload.service';

// Store the temp file in the OS temp directory — the service moves it to its final location
const upload = multer({
  dest: os.tmpdir(),
  limits: { fileSize: 100 * 1024 * 1024 }, // 100 MB max
  fileFilter(_req, file, cb) {
    const ext = path.extname(file.originalname).toLowerCase();
    if (ext !== '.zip') {
      return cb(new Error('Only .zip files are accepted'));
    }
    cb(null, true);
  },
});

export const uploadMiddleware = upload.single('file');

export async function uploadRepository(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    if (!req.file) {
      res.status(400).json({ status: 'error', message: 'No file uploaded. Send a .zip file as the "file" field.' });
      return;
    }

    // Verify the project exists and is owned by the authenticated user before saving
    await getProjectDetail(req.params.id, req.userId);

    const project = await saveUploadedFile(req.params.id, req.userId, req.file);

    res.status(200).json({ project });
  } catch (err) {
    next(err);
  }
}
