const express = require("express")
const router = new express.Router()

const errorHandler = require("../middleware/errorHandler")

const courseCtrl = require("../controllers/course")

router.get("/course", courseCtrl.getAll)

router.use("", errorHandler.handleErrors)

module.exports = router