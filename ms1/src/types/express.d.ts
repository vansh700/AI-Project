// Augments the Express Request type globally to carry the authenticated userId.
// This is set by jwt.middleware.ts after token verification.
declare namespace Express {
  interface Request {
    userId: string;
  }
}
