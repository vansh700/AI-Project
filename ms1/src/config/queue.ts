import { Queue } from 'bullmq';

// Parse the Redis URL into host/port so BullMQ's IORedis connection can use it
function parseRedisUrl(url: string): { host: string; port: number } {
  const parsed = new URL(url);
  return {
    host: parsed.hostname,
    port: parseInt(parsed.port || '6379', 10),
  };
}

const connection = parseRedisUrl(process.env.REDIS_URL ?? 'redis://localhost:6379');

// Singleton — only one Queue instance per process.
// All analysis job producers must import and use this instance.
export const analysisQueue = new Queue('analysis-queue', { connection });
