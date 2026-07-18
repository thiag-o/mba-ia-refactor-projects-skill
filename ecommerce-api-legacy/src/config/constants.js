'use strict';

/**
 * Domain constants. Extracting these removes magic literals from the business
 * logic and documents intent (P-13).
 */
module.exports = {
  // A card is approved by the (mock) gateway when its number starts with this
  // prefix. This is the demo rule the external contract depends on.
  CARD_APPROVAL_PREFIX: '4',

  PAYMENT_STATUS: {
    PAID: 'PAID',
    DENIED: 'DENIED',
  },
};
