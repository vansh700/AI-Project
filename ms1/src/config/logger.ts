import winston from 'winston';

const { combine, timestamp, json, errors, colorize, simple } = winston.format;

const isDevelopment = process.env.NODE_ENV !== 'production';

export const logger = winston.createLogger({
  level: isDevelopment ? 'debug' : 'info',
  format: combine(
    errors({ stack: true }),
    timestamp(),
    json()
  ),
  transports: [
    new winston.transports.Console({
      format: isDevelopment ? combine(colorize(), simple()) : json(),
    }),
  ],
});
