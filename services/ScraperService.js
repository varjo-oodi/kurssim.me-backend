
const osmosis = require("osmosis")

const TKT_COURSES_1 = "https://courses.helsinki.fi/fi/search/results/field_imp_organisation/tietojenk%C3%A4sittelytieteen-laitos-953/field_imp_organisation/tietojenk%C3%A4sittelytieteen-kandiohjelma-1922/field_imp_organisation/tietojenk%C3%A4sittelytieteen-maisteriohjelma-1929?search=&search=&sorting=title_field%3Aasc&items_per_page=100"
const TKT_COURSES_2 = "https://courses.helsinki.fi/fi/search/results/field_imp_organisation/tietojenk%C3%A4sittelytieteen-laitos-953/field_imp_organisation/tietojenk%C3%A4sittelytieteen-kandiohjelma-1922/field_imp_organisation/tietojenk%C3%A4sittelytieteen-maisteriohjelma-1929?academic_year=2017%20-%202018&search=&sorting=title_field%3Aasc&items_per_page=100&page=1&order=title_field&sort=asc"

module.exports = {
  getTKTCourses() {
    return Promise.all([
        this.scrapeOpintoniPage(TKT_COURSES_1),
        this.scrapeOpintoniPage(TKT_COURSES_2),
      ])
      .then(twoLists => [...twoLists[0], ...twoLists[1]])
  },
  scrapeOpintoniPage(url) {
    let courseData = []

    return new Promise((resolve, reject) => osmosis
      .get(url)
      .find("tbody")
      .set({
        id: ["tr td.views-field-field-imp-reference-to-courses-field-course-course-number"],
        name: ["tr td.views-field-title-field"],
        type: ["tr td.views-field-field-imp-reference-to-courses-field-course-type-of-teaching"],
        format: ["tr td.views-field-field-imp-method-of-study"],
        startDate: ["tr td.views-field-field-imp-begin-date"],
        teacher: ["tr td.views-field-field-imp-teacher"]
      })
      .data(data => {
        courseData = data.id.map((id, index) => {
          return {
            id,
            name: data.name[index],
            type: data.type[index],
            format: data.format[index],
            startDate: data.startDate[index],
            teacher: data.teacher[index],
          }
        })
      })
      .done(() => resolve(courseData))
    )
  }
}