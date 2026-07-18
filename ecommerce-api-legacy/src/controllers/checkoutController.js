'use strict';

const { BadRequestError } = require('../errors/AppError');

/**
 * Checkout controller: validates HTTP input, delegates to the service and
 * shapes the response. No business rules or SQL here.
 *
 * External contract preserved:
 *   - request body fields: usr, eml, pwd, c_id, card
 *   - success response: 200 { msg: "Sucesso", enrollment_id }
 */
class CheckoutController {
  constructor({ checkoutService }) {
    this.checkoutService = checkoutService;
    this.handle = this.handle.bind(this);
  }

  async handle(req, res) {
    const { usr, eml, pwd, c_id: courseId, card } = req.body || {};

    if (!usr || !eml || !courseId || !card) {
      throw new BadRequestError('Bad Request');
    }

    const { enrollmentId } = await this.checkoutService.checkout({
      name: usr,
      email: eml,
      password: pwd,
      courseId,
      card,
    });

    res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
  }
}

module.exports = CheckoutController;
