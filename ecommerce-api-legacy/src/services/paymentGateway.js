'use strict';

const { CARD_APPROVAL_PREFIX, PAYMENT_STATUS } = require('../config/constants');

/**
 * Encapsulates the payment authorization rule behind a gateway abstraction
 * (P-04/P-13). The card number and gateway key are NEVER logged — only the
 * amount and the last four digits are recorded.
 */
class PaymentGateway {
  constructor({ apiKey, logger }) {
    this.apiKey = apiKey;
    this.logger = logger;
  }

  authorize(card, amount) {
    this.logger.info('Authorizing payment', {
      amount,
      last4: String(card).slice(-4),
    });

    const approved = String(card).startsWith(CARD_APPROVAL_PREFIX);
    return {
      approved,
      status: approved ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED,
    };
  }
}

module.exports = PaymentGateway;
