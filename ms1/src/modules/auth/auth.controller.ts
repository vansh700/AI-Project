import { Request, Response, NextFunction } from 'express';
import { registerSchema, loginSchema } from './auth.validation';
import { registerUser, loginUser } from './auth.service';

export async function register(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const dto = registerSchema.parse(req.body);
    const token = await registerUser(dto);
    res.status(201).json({ token });
  } catch (err) {
    next(err);
  }
}

export async function login(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const dto = loginSchema.parse(req.body);
    const token = await loginUser(dto);
    res.status(200).json({ token });
  } catch (err) {
    next(err);
  }
}
