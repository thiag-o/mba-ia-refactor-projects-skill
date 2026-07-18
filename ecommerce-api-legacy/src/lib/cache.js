'use strict';

/**
 * Simple injectable cache abstraction backed by a Map. Replaces the module-level
 * mutable `globalCache`/`totalRevenue` singletons (P-06): each instance is
 * created and injected via the composition root instead of shared global state.
 */
class Cache {
  constructor() {
    this.store = new Map();
  }

  set(key, value) {
    this.store.set(key, value);
  }

  get(key) {
    return this.store.get(key);
  }

  has(key) {
    return this.store.has(key);
  }

  delete(key) {
    return this.store.delete(key);
  }
}

module.exports = Cache;
