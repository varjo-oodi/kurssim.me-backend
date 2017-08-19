
const fetch = require("node-fetch")

let cachedGets = {}

function getFromCache(params) {
  if (cachedGets[params.url] && cachedGets[params.url].timeStamp < Date.now() + 30 * 60 * 1000) { // 30 min
    return cachedGets[params.url].result
  }
  return undefined
}

function setToCache(params, json) {
  cachedGets[params.url] = {}
  cachedGets[params.url].result = json
  cachedGets[params.url].timeStamp = Date.now()
}

module.exports = {
  get(params) {
    const cached = getFromCache(params)
    if (cached) return cached
    return fetch(`${process.env.WEBOODI_API_URL}/hae?${params.url}`, {
      method: "get",
      headers: {
        Accept: "application/json",
      }
    }).then(res => res.json())
    .then(json => {
      setToCache(params, json)
      return json
    })
  }
}