
const RequestService = require("../services/RequestService")
const ScraperService = require("../services/ScraperService")

/*
Weboodi kurssi
{
  "lahde": "opetustapahtumat",
  "opintokohde": {
    "opintokohdeId": 102679660,
    "opintokohteenTunniste": "582221",
    "opintokohteenNimi": "Aineopintojen harjoitustyö: Ohjelmointi",
    "laajuus": 0,
    "vastuuorganisaationNimi": "Tietojenkäsittelytieteen laitos",
    "ilmoittautumiskelpoinen": false,
    "laajuusOp": 5,
    "selite": null,
    "maksimilaajuus": 0,
    "maksimilaajuusOp": 5
  },
  "opetustapahtumat": [
    {
      "opetustapahtumaId": 119282686,
      "opintokohdeId": 102679660,
      "opintokohteenTunniste": "582221",
      "opintokohteenNimi": "Aineopintojen harjoitustyö: Ohjelmointi",
      "opetustapahtumanNimi": "Aineopintojen harjoitustyö: Ohjelmointi (loppukesä)",
      "opetustapahtumanTyyppiSelite": "Laboratoriotyö",
      "laajuus": 0,
      "vastuuopettaja": "<a href=mailto:matti.luukkainen@helsinki.fi>Matti Luukkainen</a>",
      "alkuPvm": 1500843600000,
      "loppuPvm": 1504213200000,
      "vastuuorganisaatioId": -2,
      "vastuuorganisaationNimi": null,
      "paaAlkuPvm": -61220109600000,
      "laajuusOp": 5,
      "alkuperainenLaajuus": 1,
      "tentti": false,
      "tila": "ilmoittautuminen_kaynnissa",
      "ilmAlkPvm": null,
      "ilmPaatPvm": 1504213140000,
      "showToStudents": true,
      "ilmoittautumiskelpoinen": true
    }
  ]
}

Weboodi opetustapahtuma, x represents values that are picked from it

x "opetustapahtumaId": 119282686,
x "opintokohdeId": 102679660,
x "opintokohteenTunniste": "582221",
"opintokohteenNimi": "Aineopintojen harjoitustyö: Ohjelmointi",
x "opetustapahtumanNimi": "Aineopintojen harjoitustyö: Ohjelmointi (loppukesä)",
x "opetustapahtumanTyyppiSelite": "Laboratoriotyö",
"laajuus": 0,
"vastuuopettaja": "<a href=mailto:matti.luukkainen@helsinki.fi>Matti Luukkainen</a>",
x "alkuPvm": 1500843600000,
x "loppuPvm": 1504213200000,
"vastuuorganisaatioId": -2,
"vastuuorganisaationNimi": null,
"paaAlkuPvm": -61220109600000,
x "laajuusOp": 5,
"alkuperainenLaajuus": 1,
"tentti": false,
"tila": "ilmoittautuminen_kaynnissa",
x "ilmAlkPvm": null,
x "ilmPaatPvm": 1504213140000,
"showToStudents": true,
x "ilmoittautumiskelpoinen": true
*/

function combineStudyEvents(opintoniEvent, oodiEvent) {
  return {
    parentId: oodiEvent.opintokohdeId,
    id: oodiEvent.opetustapahtumaId,
    tag: oodiEvent.opintokohteenTunniste,
    name: oodiEvent.opetustapahtumanNimi,
    type: opintoniEvent.type,
    format: opintoniEvent.format,
    teachers: opintoniEvent.teachers,
    opintoniLink: opintoniEvent.link,
    credits: oodiEvent.laajuusOp,
    open: oodiEvent.ilmoittautumiskelpoinen,
    opintoniStartDate: opintoniEvent.opintoniStartDate,
    startDate: oodiEvent.alkuPvm,
    endDate: oodiEvent.loppuPvm,
    enrolmentStartDate: oodiEvent.ilmAlkPvm,
    enrolmentEndDate: oodiEvent.ilmPaatPvm,
  }
}

const joinOodiCoursesToOpintoni = (opintoniCourses, oodiCourses) => (
  opintoniCourses
    .reduce((acc, opintoniCourse) => {
      // Find the oodi opintokohde with the same tag
      const oodiCourse = oodiCourses.find(c => c.opintokohde.opintokohteenTunniste === opintoniCourse.tag)

      if (!oodiCourse) {
        return acc
      }

      const combinedCourse = opintoniCourse.events.map(opintoniEvent => {
        // Parse id from the link -> https://courses.helsinki.fi/fi/tkt10003/119284733 -> 119284733
        const eventId = parseInt(opintoniEvent.link.substring(opintoniEvent.link.lastIndexOf("/") + 1))
        // Find the oodi event with the same id
        const oodiEvent = oodiCourse.opetustapahtumat.find(event => event.opetustapahtumaId === eventId)
        if (oodiEvent) {
          return combineStudyEvents(opintoniEvent, oodiEvent)
        } else {
          // This means that the Opintoni-event isn't in Weboodi most probably because it has expired
          return { ...opintoniEvent, id: eventId, expired: true }
        }
      })

      return [...acc, ...combinedCourse]
    }, [])
)

module.exports = {
  async getAll(req, res, next) {
    try {
      const opintoniCourses = await ScraperService.getTKTCourses()
      const oodiCourses = await RequestService.getTKTCourses()
      const combinedCourses = joinOodiCoursesToOpintoni(opintoniCourses, oodiCourses)

      res.json({ courses: combinedCourses })
    } catch (err) {
      next(err)
    }
  }
}