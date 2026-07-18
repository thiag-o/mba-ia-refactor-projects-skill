'use strict';

/**
 * User persistence. All SQL touching the `users` table lives here (MVC: Model).
 * The DB connection is injected — the model never creates it (DIP).
 */
class UserModel {
  constructor(db) {
    this.db = db;
  }

  findByEmail(email) {
    return this.db.get('SELECT * FROM users WHERE email = ?', [email]);
  }

  findById(id) {
    return this.db.get('SELECT * FROM users WHERE id = ?', [id]);
  }

  async create({ name, email, passwordHash }) {
    const result = await this.db.run(
      'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
      [name, email, passwordHash],
    );
    return result.lastID;
  }

  deleteById(id) {
    return this.db.run('DELETE FROM users WHERE id = ?', [id]);
  }

  /**
   * Serializer that strips the sensitive `pass` field. A model must never
   * expose the password/hash to the outside world.
   */
  static toPublic(user) {
    if (!user) {
      return null;
    }
    const { pass, ...safeFields } = user;
    return safeFields;
  }
}

module.exports = UserModel;
