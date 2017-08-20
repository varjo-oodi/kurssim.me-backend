
const fetch = require("node-fetch")

module.exports = {
  getTKTCourses() {
    return Promise.all([
      this.get({ url: "vastuuorganisaatio=1000000921" }), // Tietojenkäsittelytieteen laitos
      this.get({ url: "vastuuorganisaatio=116716376" }), // Tietojenkäsittelytieteen kandiohjelma
      this.get({ url: "vastuuorganisaatio=116738259" }), // Tietojenkäsittelytieteen maisteriohjelma
      this.get({ url: "vastuuorganisaatio=116710672" }), // Datatieteen maisteriohjelma
    ])
    // Combine 4 lists into one giant list (15k lines)
    .then(orgs => orgs.reduce((acc, org) => [...acc, ...org], []))
  },
  get(params) {
    return fetch(`${process.env.WEBOODI_API_URL}/hae?${params.url}`, {
      method: "get",
      headers: {
        Accept: "application/json",
      }
    })
    .then(res => res.json())
  }
}