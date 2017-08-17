
const RequestService = require("../services/RequestService")

module.exports = {
  async getAll(req, res, next) {
    try {
      const courses = await RequestService.get({
        url: "opas=5323",
      })
      res.json(courses)
    } catch (err) {
      next(err)
    }
  }
}