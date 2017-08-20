const express = require("express")
const router = new express.Router()

const apicache = require("apicache")
const cache = apicache.middleware

const errorHandler = require("../middleware/errorHandler")

const courseCtrl = require("../controllers/course")

router.get("/course", cache("30 minutes"), courseCtrl.getAll)

router.use("", errorHandler.handleErrors)

module.exports = router