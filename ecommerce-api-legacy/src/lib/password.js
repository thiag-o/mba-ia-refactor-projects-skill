'use strict';

const crypto = require('crypto');
const { promisify } = require('util');

/**
 * Secure, salted password hashing using Node's built-in scrypt KDF — no new
 * runtime dependency required (P-05). Replaces the homemade, unsalted
 * `badCrypto` hash. Passwords are never stored in plaintext and never returned.
 */
const scrypt = promisify(crypto.scrypt);

const KEY_LENGTH = 64;
const SALT_LENGTH = 16;

async function hashPassword(plainPassword) {
  if (!plainPassword) {
    throw new Error('A password is required to hash');
  }
  const salt = crypto.randomBytes(SALT_LENGTH).toString('hex');
  const derivedKey = await scrypt(plainPassword, salt, KEY_LENGTH);
  return `${salt}:${derivedKey.toString('hex')}`;
}

async function verifyPassword(plainPassword, storedHash) {
  if (!plainPassword || !storedHash) {
    return false;
  }
  const [salt, key] = storedHash.split(':');
  if (!salt || !key) {
    return false;
  }
  const derivedKey = await scrypt(plainPassword, salt, KEY_LENGTH);
  const keyBuffer = Buffer.from(key, 'hex');
  if (keyBuffer.length !== derivedKey.length) {
    return false;
  }
  return crypto.timingSafeEqual(keyBuffer, derivedKey);
}

module.exports = { hashPassword, verifyPassword };
