import { User } from '@prisma/client';
import { prisma } from '../../config/prisma.client';

export async function findUserByEmail(email: string): Promise<User | null> {
  return prisma.user.findUnique({ where: { email } });
}

export async function createUser(email: string, passwordHash: string): Promise<User> {
  return prisma.user.create({ data: { email, passwordHash } });
}
