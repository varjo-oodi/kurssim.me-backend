
const scrapeIt = require("scrape-it")

// TODO Change year dynamically? Now set to 2017-2018
const TKT_COURSES_1 = "https://courses.helsinki.fi/fi/search/results/field_imp_organisation/tietojenk%C3%A4sittelytieteen-maisteriohjelma-1929/field_imp_organisation/datatieteen-maisteriohjelma-1931/field_imp_organisation/tietojenk%C3%A4sittelytieteen-laitos-953/field_imp_organisation/tietojenk%C3%A4sittelytieteen-kandiohjelma-1922?search=&search=&sorting=title_field%3Aasc&items_per_page=100&order=title_field&sort=asc"
const TKT_COURSES_2 = "https://courses.helsinki.fi/fi/search/results/field_imp_organisation/tietojenk%C3%A4sittelytieteen-maisteriohjelma-1929/field_imp_organisation/datatieteen-maisteriohjelma-1931/field_imp_organisation/tietojenk%C3%A4sittelytieteen-laitos-953/field_imp_organisation/tietojenk%C3%A4sittelytieteen-kandiohjelma-1922?academic_year=2017%20-%202018&search=&sorting=title_field%3Aasc&items_per_page=100&page=1&order=title_field&sort=asc"

module.exports = {
  getTKTCourses() {
    return Promise.all([
        this.scrapeOpintoniPage(TKT_COURSES_1),
        this.scrapeOpintoniPage(TKT_COURSES_2),
      ])
      .then(pages => [...pages[0], ...pages[1]])
  },
  scrapeOpintoniPage(url) {
    return scrapeIt(url, {
      courses: {
        listItem: "tbody tr",
        data: {
          link: {
            selector: "td a",
            attr: "href"
          },
          tag: "td.views-field-field-imp-reference-to-courses-field-course-course-number",
          name: "td.views-field-title-field",
          type: "td.views-field-field-imp-reference-to-courses-field-course-type-of-teaching",
          format: "td.views-field-field-imp-method-of-study",
          startDate: "td.views-field-field-imp-begin-date",
          teachers: {
            selector: "td.views-field-field-imp-teacher",
            convert: x => x.split(", ")
          }
        }
      }
    })
     // There is sometimes empty rows (<tr>) inside the html list because of lazy coding on their part
    .then(page => page.courses.filter(course => course.link))
    // Turn 
    // Combine courses with same tag into one course
    .then(courses => {
      const processedTags = []
      return courses.reduce((acc, course, index) => {
        if (processedTags.indexOf(course.tag) === -1) {
          const sameCourses = findCoursesWithSameTag(courses, index, course.tag)
          processedTags.push(...sameCourses[0])
          const rootCourse = {
            tag: course.tag,
            name: course.name,
            type: course.type,
            events: sameCourses[1]
          }
          acc.push(rootCourse)
        }
        return acc
      }, [])
    })
  }
}

function findCoursesWithSameTag(courses, index, tag) {
  let processedTags = [tag], foundCourses = []
  while(courses.length !== index && courses[index].tag === tag) {
    foundCourses.push(courses[index])
    processedTags.push(courses[index].tag)
    index++
  }
  return [processedTags, foundCourses]
}