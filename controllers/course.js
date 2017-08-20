
const RequestService = require("../services/RequestService")
const ScraperService = require("../services/ScraperService")

module.exports = {
  async getAll(req, res, next) {
    try {
      const scrapedCourses = await ScraperService.getTKTCourses()
      console.log(scrapedCourses.length)
      // console.log(scrapedCourses)
      // const courses = await RequestService.get({
      //   url: "vastuuorganisaatio=1000000921", // on koko TKTn laitos
      // })
      // const bachelorCourses = await RequestService.get({
      //   url: "opas=5323",
      // })
      // const masterCourses = await RequestService.get({
      //   url: "opas=5351",
      // })
      res.json({ courses, bachelorCourses, masterCourses, })
    } catch (err) {
      next(err)
    }
  }
}