'use strict';

const sqlite3 = require('sqlite3').verbose();

/**
 * Promise-based wrapper around the callback-driven sqlite3 driver so the rest
 * of the codebase can use async/await instead of nested callbacks (P-10).
 * The connection is created here and injected into models via the composition
 * root — nothing instantiates its own database (P-06).
 */
class Database {
  constructor(filename) {
    this.connection = new sqlite3.Database(filename);
  }

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.run(sql, params, function onComplete(err) {
        if (err) {
          return reject(err);
        }
        return resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.get(sql, params, (err, row) => {
        if (err) {
          return reject(err);
        }
        return resolve(row);
      });
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.all(sql, params, (err, rows) => {
        if (err) {
          return reject(err);
        }
        return resolve(rows);
      });
    });
  }

  exec(sql) {
    return new Promise((resolve, reject) => {
      this.connection.exec(sql, (err) => {
        if (err) {
          return reject(err);
        }
        return resolve();
      });
    });
  }

  close() {
    return new Promise((resolve, reject) => {
      this.connection.close((err) => {
        if (err) {
          return reject(err);
        }
        return resolve();
      });
    });
  }
}

function createDatabase(filename) {
  return new Database(filename);
}

module.exports = { Database, createDatabase };
