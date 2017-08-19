
const RequestService = require("../services/RequestService")

module.exports = {
  async getAll(req, res, next) {
    try {
      const courses = await RequestService.get({
        url: "vastuuorganisaatio=1000000921", // on koko TKTn laitos
      })
      const bachelorCourses = await RequestService.get({
        url: "opas=5323",
      })
      const masterCourses = await RequestService.get({
        url: "opas=5351",
      })
      res.json({ courses, bachelorCourses, masterCourses, })
    } catch (err) {
      next(err)
    }
  }
}