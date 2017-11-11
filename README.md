
# [kurssim.me](https://kurssim.me) backend [![Build Status](https://travis-ci.org/varjo-oodi/kurssim.me-backend.svg?branch=master)](https://travis-ci.org/varjo-oodi/kurssim.me-backend)

1) Install Node.js version >=8 using nvm
2) Download this repo and enter `npm i`
3) Copy the development variables to .env -file `cp .env.development .env`
4) Run the development server `npm run nodemon`

http://localhost:8000/course

## Scraper

### How to run
1) Install scrapy: `pip install scrapy` (or `pip3` if you have both Python2 and Python3)
2) Run: `scrapy crawl opintoni_spider`

This will start the scraper and output the courses into a folder `output` as line-delimited json.