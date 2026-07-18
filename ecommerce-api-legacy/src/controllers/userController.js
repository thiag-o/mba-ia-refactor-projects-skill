'use strict';

/**
 * User controller. Handles the destructive delete route, delegating cascade
 * cleanup to the service.
 */
class UserController {
  constructor({ userService }) {
    this.userService = userService;
    this.remove = this.remove.bind(this);
  }

  async remove(req, res) {
    await this.userService.deleteUser(req.params.id);
    res.status(200).json({ msg: 'Usuário deletado' });
  }
}

module.exports = UserController;
