
const fetch = require("node-fetch")

module.exports = {
  get(params) {
    return fetch(`${process.env.WEBOODI_API_URL}/hae?${params.url}`, {
      method: "get",
      headers: {
        Accept: "application/json",
      }
    }).then(res => res.json())
  }
}