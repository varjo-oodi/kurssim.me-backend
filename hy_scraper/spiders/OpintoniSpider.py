import scrapy

from hy_scraper.items import CourseItem

class OpintoniSpider(scrapy.Spider):
  name = 'opintoni_spider'
  start_urls = ['https://courses.helsinki.fi/fi/search/results/field_imp_organisation/datatieteen-maisteriohjelma-1931/field_imp_organisation/tietojenk%C3%A4sittelytieteen-kandiohjelma-1922/field_imp_organisation/tietojenk%C3%A4sittelytieteen-maisteriohjelma-1929/field_imp_organisation/tietojenk%C3%A4sittelytieteen-laitos-953?&search=&academic_year=2017%20-%202018']
  start_fields = ['tkt_kandi', 'tkt_maisteri', 'tktl', 'data_maisteri']

  def parse(self, response):
    for i, tr in enumerate(response.css('div#kuvat a')):
      label = tr.css('')
      name = tr.css('')
      type = tr.css('')
      start_date = tr.css('')
      teachers = tr.css('')
      course_url = response.urljoin(img_link.css('::attr(href)').extract_first().strip())
      yield response.follow(course_url) # add course-info as meta-data
    
    yield response.follow() # next page with "Seuraava"!

  def parse_course():
    label = 1
    type = 2
    op = 3
    # teachers
    start_date = 4
    end_date = 5
    enroll_start_date = 6
    enroll_end_date = 7
    schedule = 8 # ? list of lectures if luentoKurssi, date of exam if tentti
    opintoni_url = 9
    oodi_url = 9.1
    moodle_url = 10 # ?

  def parse_oodi_course():
    study_groups = 1 # list of study-groups with current enrollment and the teacher and schedule
    enrollment = 2 # ? amount of currently enrolled students