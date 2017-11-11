import scrapy

from hy_scraper.items import CourseItem

def strip(text):
  if text: return text.strip()
  else: return ''

def strip_list(text):
  if text: return text.strip()
  else: return ''

class OpintoniSpider(scrapy.Spider):
  name = 'opintoni_spider'
  start_urls = [
    'https://courses.helsinki.fi/fi/search/results/field_imp_organisation/matemaattis-luonnontieteellinen-tiedekunta-942/field_imp_organisation/tietojenk%C3%A4sittelytieteen-kandiohjelma-1922?search=&academic_year=2017%20-%202018',
    # 'https://courses.helsinki.fi/fi/search/results/field_imp_organisation/matemaattis-luonnontieteellinen-tiedekunta-942/field_imp_organisation/tietojenk%C3%A4sittelytieteen-maisteriohjelma-1929?search=&academic_year=2017%20-%202018',
    # 'https://courses.helsinki.fi/fi/search/results/field_imp_organisation/matemaattis-luonnontieteellinen-tiedekunta-942/field_imp_organisation/datatieteen-maisteriohjelma-1931?search=&academic_year=2017%20-%202018'
  ]
  start_fields = ['tkt_kandi', 'tkt_maisteri', 'data_maisteri']

  def parse(self, response):
    for tr in response.css('tbody tr'):
      course_dict = {
        'tag': tr.css('td.views-field-field-imp-reference-to-courses-field-course-course-number ::text').extract_first().strip(),
        'name': tr.css('td.views-field-title-field a ::text').extract_first().strip(),
        'opintoni_url': response.urljoin(tr.css('td.views-field-title-field a ::attr(href)').extract_first().strip()),
        'type': tr.css('td.views-field-field-imp-reference-to-courses-field-course-type-of-teaching ::text').extract_first().strip(),
        'format': tr.css('td.views-field-field-imp-method-of-study ::text').extract_first().strip(),
        'teachers': strip(tr.css('td.views-field-field-imp-teacher ::text').extract_first())
      }
      url_chunks = course_dict['opintoni_url'].split('/')
      course_dict['id'] = url_chunks[len(url_chunks) - 1]
      print(course_dict)
      yield response.follow(course_dict['opintoni_url'], self.parse_opintoni_course, meta={'course': course_dict})
      
    next_url = response.urljoin(response.css('li.pager__next a::attr(href)').extract_first().strip())
    yield response.follow(next_url) # next page with 'Seuraava'!

  def parse_opintoni_course(self, response):
    course = response.meta['course']

    courses_info = response.css('span.course-info ::text').extract()
    # Ridiculously coded course_info element that is the following structure:
    # <span class="course-info">
    #   <a href="/fi/tkt10002" class="GoogleAnalyticsET-processed">TKT10002</a>, Luentokurssi, 5 op,
    #   <span>Arto Hellas</span>, 05.09.2017 - 17.10.2017
    # </span>
    credits = courses_info[1].strip()
    date = courses_info[3].strip()
    print('credits: {} date: {}'.format(credits, date))

    # There is enrollment dates for SOME courses on Opintoni-page, not all
    # So better way is to scrape the enrollment from Weboodi as that piece of shit actually always shows the date
    # enrollment = response.css('div.button.button--info.button__inline.icon--time ::text').extract_first().strip()
    # Enrollment is eg. 11.12.2017 klo 09:00 - 2.5.2018 klo 23:59 or None

    # Weboodi URLs are eg. https://weboodi.helsinki.fi/hy/opettaptied.jsp?OpetTap=121540795&Kieli=1&Tunniste=TKT10005
    # And some courses show the link but often if it's in far future, not
    oodi_url = 'https://weboodi.helsinki.fi/hy/opettaptied.jsp?OpetTap={}&Kieli=1&Tunniste={}'.format(course['id'], course['tag'])

    # teachers
    start_date = 4
    end_date = 5
    schedule = 8 # ? list of lectures if luentoKurssi, date of exam if tentti
    opintoni_url = 9
    oodi_url = 9.1
    moodle_url = 10 # ?

    yield CourseItem(course)
    # yield response.follow(course['oodi_url'], self.parse_oodi_course, meta={'course': course})

  def parse_oodi_course(self, response):
    course = response.meta['course']

    # >_< wtf really...
    bottom_tables = response.css('section form table')
    # Might have enrollment dates, might have amount of enrollments, 
    first_enroll_table = bottom_tables[3]
    enroll_start_date = 6
    enroll_end_date = 7
    enrolled = 8
    max_enroll = 9
    schedule = 10
    course_languages = 11

    first_schedule_table = bottom_tables[6]

    # The rest are group tables (?)
    for table in bottom_tables:
      enrollment = 1
      enrolled = 2
      max_enroll = 3
      group_name = 4
      group_teacher = 5
      group_schedule = 6
      group_languages = 7

    yield CourseItem(course)