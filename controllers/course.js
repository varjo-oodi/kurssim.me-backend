
const RequestService = require("../services/RequestService")

module.exports = {
  async getAll(req, res, next) {
    try {
      const courses = await RequestService.get({
        // url: "opas=5323",
        url: "nimiTaiTunniste=TKT&opas=5323&lukukausi=135",        
      })
      res.json({ courses, })
    } catch (err) {
      next(err)
    }
  }
}