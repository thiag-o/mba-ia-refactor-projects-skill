'use strict';

/**
 * Minimal structured logger with levels and automatic redaction of sensitive
 * fields. Replaces the scattered console.log calls and prevents secrets/card
 * numbers from leaking into logs (P-08, replaces AP logging smell).
 */
const LEVELS = { error: 0, warn: 1, info: 2, debug: 3 };

const SENSITIVE_KEY_PATTERNS = [
  /pass/i,
  /pwd/i,
  /secret/i,
  /token/i,
  /key/i,
  /card/i,
  /authorization/i,
];

function redact(meta) {
  if (!meta || typeof meta !== 'object') {
    return meta;
  }
  const output = Array.isArray(meta) ? [] : {};
  for (const [key, value] of Object.entries(meta)) {
    if (SENSITIVE_KEY_PATTERNS.some((pattern) => pattern.test(key))) {
      output[key] = '[REDACTED]';
    } else if (value && typeof value === 'object') {
      output[key] = redact(value);
    } else {
      output[key] = value;
    }
  }
  return output;
}

function createLogger(level = 'info') {
  const threshold = LEVELS[level] ?? LEVELS.info;

  function write(logLevel, message, meta) {
    if (LEVELS[logLevel] > threshold) {
      return;
    }
    const entry = {
      timestamp: new Date().toISOString(),
      level: logLevel,
      message,
    };
    if (meta !== undefined) {
      entry.meta = redact(meta);
    }
    const line = JSON.stringify(entry);
    if (logLevel === 'error') {
      process.stderr.write(`${line}\n`);
    } else {
      process.stdout.write(`${line}\n`);
    }
  }

  return {
    error: (message, meta) => write('error', message, meta),
    warn: (message, meta) => write('warn', message, meta),
    info: (message, meta) => write('info', message, meta),
    debug: (message, meta) => write('debug', message, meta),
  };
}

module.exports = createLogger;
