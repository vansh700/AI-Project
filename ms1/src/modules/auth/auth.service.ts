import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { findUserByEmail, createUser } from './user.repository';
import { RegisterDto, LoginDto } from './auth.validation';

const SALT_ROUNDS = 12;

export async function registerUser(dto: RegisterDto): Promise<string> {
  const existing = await findUserByEmail(dto.email);
  if (existing) {
    throw Object.assign(new Error('Email already registered'), { statusCode: 409 });
  }

  const passwordHash = await bcrypt.hash(dto.password, SALT_ROUNDS);
  const user = await createUser(dto.email, passwordHash);

  return signToken(user.id);
}

export async function loginUser(dto: LoginDto): Promise<string> {
  const user = await findUserByEmail(dto.email);

  // Deliberately vague error — prevents email enumeration attacks
  if (!user) {
    throw Object.assign(new Error('Invalid credentials'), { statusCode: 401 });
  }

  const valid = await bcrypt.compare(dto.password, user.passwordHash);
  if (!valid) {
    throw Object.assign(new Error('Invalid credentials'), { statusCode: 401 });
  }

  return signToken(user.id);
}

function signToken(userId: string): string {
  return jwt.sign({ userId }, process.env.JWT_SECRET as string, { expiresIn: '7d' });
}
