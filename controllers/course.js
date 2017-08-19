
const RequestService = require("../services/RequestService")

module.exports = {
  async getAll(req, res, next) {
    try {
      const bachelorCourses = await RequestService.get({
        url: "opas=5323",
      })
      const masterCourses = await RequestService.get({
        url: "opas=5351",
      })
      res.json({ bachelorCourses, masterCourses, })
    } catch (err) {
      next(err)
    }
  }
}