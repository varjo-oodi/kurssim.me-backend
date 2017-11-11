import scrapy

from scrapy.http.request import Request
from hy_scraper.items import CourseItem

def strip(text):
  return text.strip() if text else ''

def strip_list(text):
  return [strip(x) for x in text.split(',')]

# Eg. '\r\r10.10.17\r\n        klo 09.00-\r\r'
def strip_date(text):
  chunks = strip(text).split(' ')
  return strip(chunks[0])

# Eg. '\r\n                            30.10.2017 -19.11.2017\r\n                        '
# Or: '\r\n                            30.10.2017\r\n                        '
def strip_date_range(text):
  return [strip(x) for x in strip(text).split('-')]
  # chunks = strip(text).split('-')
  # if len(chunks) == 1:
  #   return [strip(chunks[0])]
  # return [strip(chunks[0]), strip(chunks[1])]

# Eg. ['\r\n                \r\n                08.11.17\r\n                klo 09.00-', '\r\n                28.11.17\r\n                klo 23.59\r\n                \r\n                \r\n                \r\n            ']
def strip_date_chunks(chunks):
  return [strip_date(date) for date in chunks]

# Eg. '5 op' or ' 5 op / 0 ov '
def strip_credits(text):
  return parseInt(text.split('op')[0])

def get_enrollment_dates(dates, groups):
  if len(dates) == 2:
    return dates
  elif len(groups) > 0:
    # All groups if course doesn't have dates should have enrollment_dates...
    return [groups[0]['enrollment_start_date'], groups[0]['enrollment_end_date']]
  return []

# https://gist.github.com/douglasmiranda/2174255
def parseInt(string):
  return int(''.join([x for x in string if x.isdigit()])) if string else ''

class OpintoniSpider(scrapy.Spider):
  name = 'opintoni_spider'
  start_urls = [
    'https://courses.helsinki.fi/fi/search/results/field_imp_organisation/matemaattis-luonnontieteellinen-tiedekunta-942/field_imp_organisation/tietojenk%C3%A4sittelytieteen-kandiohjelma-1922?search=&academic_year=2017%20-%202018',
    'https://courses.helsinki.fi/fi/search/results/field_imp_organisation/matemaattis-luonnontieteellinen-tiedekunta-942/field_imp_organisation/tietojenk%C3%A4sittelytieteen-maisteriohjelma-1929?search=&academic_year=2017%20-%202018',
    'https://courses.helsinki.fi/fi/search/results/field_imp_organisation/matemaattis-luonnontieteellinen-tiedekunta-942/field_imp_organisation/datatieteen-maisteriohjelma-1931?search=&academic_year=2017%20-%202018'
  ]
  start_fields = ['tkt_kandi', 'tkt_maisteri', 'data_maisteri']

  def start_requests(self):
    for i, url in enumerate(self.start_urls):
      yield Request(url, self.parse, meta={'study_field': self.start_fields[i]})

  def parse(self, response):
    for tr in response.css('tbody tr'):
      course_dict = {
        'study_field': response.meta['study_field'],
        'tag': tr.css('td.views-field-field-imp-reference-to-courses-field-course-course-number ::text').extract_first().strip(),
        'name': tr.css('td.views-field-title-field a ::text').extract_first().strip(),
        'opintoni_url': response.urljoin(tr.css('td.views-field-title-field a ::attr(href)').extract_first().strip()),
        'type': tr.css('td.views-field-field-imp-reference-to-courses-field-course-type-of-teaching ::text').extract_first().strip(),
        'format': tr.css('td.views-field-field-imp-method-of-study ::text').extract_first().strip(),
        'teachers': strip_list(tr.css('td.views-field-field-imp-teacher ::text').extract_first())
      }
      url_chunks = course_dict['opintoni_url'].split('/')
      course_dict['id'] = parseInt(url_chunks[len(url_chunks) - 1])
      # print(course_dict)
      yield response.follow(course_dict['opintoni_url'], self.parse_opintoni_course, meta={'course': course_dict})
      
    next_url = response.urljoin(strip(response.css('li.pager__next a::attr(href)').extract_first()))
    yield response.follow(next_url) # next page with 'Seuraava'

  def parse_opintoni_course(self, response):
    course = response.meta['course']

    courses_info = response.css('span.course-info ::text').extract()
    # Ridiculously coded course_info element that is the following structure:
    # <span class="course-info">
    #   <a href="/fi/tkt10002" class="GoogleAnalyticsET-processed">TKT10002</a>, Luentokurssi, 5 op,
    #   <span>Arto Hellas</span>, 05.09.2017 - 17.10.2017
    # </span>

    # There is enrollment dates for SOME courses on Opintoni-page, not all
    # So better way is to scrape the enrollment from Weboodi as that piece of shit actually always shows the date
    # enrollment = response.css('div.button.button--info.button__inline.icon--time ::text').extract_first().strip()
    # Enrollment is eg. 11.12.2017 klo 09:00 - 2.5.2018 klo 23:59 or None

    # Weboodi URLs are eg. https://weboodi.helsinki.fi/hy/opettaptied.jsp?OpetTap=121540795&Kieli=1
    # And some courses show the link but often if it's in far future, not
    course['oodi_url'] = 'https://weboodi.helsinki.fi/hy/opettaptied.jsp?OpetTap={}&Kieli=1'.format(course['id'])

    schedule = 8 # ? list of lectures if luentoKurssi, date of exam if tentti
    moodle_url = 10 # ?

    yield response.follow(course['oodi_url'], self.parse_oodi_course, meta={'course': course})

  # This is nightmare. Weboodi is crap, inside out. This is the logic for extracting the course information.
  def parse_oodi_course(self, response):
    course = response.meta['course']

    top_tables = response.css('section#legacy-page-wrapper').xpath('*/table//table')
    info_trs = top_tables[0].css('tr')
    # 3 has the Credits
    credits = strip_credits(info_trs[1].css('td')[1].css('::text').extract_first())
    # 5 has the Date
    course_dates = strip_date_range(info_trs[3].css('td')[1].css('::text').extract_first())
    start_date = course_dates[0]
    end_date = course_dates[1] if len(course_dates) > 1 else ''
    # print('credits: {} , date: {}'.format(credits, course_dates))

    # Not all courses have groups eg. exams
    group_table = response.css('table.kll')
    groups = self.scrape_oodi_groups(group_table)

    # Funnily enough this should be an unique element
    main_dates = strip_date_chunks(response.css('td[width="13%"] td[nowrap]::text').extract())
    # If main_dates are empty use group dates for enrollment dates
    main_dates = get_enrollment_dates(main_dates, groups)
    enrollment_start_date = main_dates[0] if len(main_dates) == 2 else ''
    enrollment_end_date = main_dates[1] if len(main_dates) == 2 else ''

    course['credits'] = credits
    course['start_date'] = start_date
    course['end_date'] = end_date
    course['enrollment_start_date'] = enrollment_start_date
    course['enrollment_end_date'] = enrollment_end_date
    course['groups'] = groups
    # print(groups)
    yield CourseItem(course)

  def scrape_oodi_groups(self, table):
    group_list = []
    groups = table.xpath('*')
    for i, group in enumerate(groups):
      # First element is just the header table
      if i == 0: continue
      blocks = group.xpath('*')
      first_block = blocks[0]

      # Contains enrolled/max as string eg. '50/50' or '0/-'
      enrollment = first_block.css('td[width="14%"]::text').extract_first().strip()
      enrollment_chunks = enrollment.split('/')
      enrolled = parseInt(enrollment_chunks[0])
      enrollment_max = parseInt(enrollment_chunks[1])

      # Contains two strings with enrollment dates:
      # ['02.10.17\r\n        klo 09.00-', '15.12.17\r\n        klo 23.59']
      enrollment_dates = strip_date_chunks(first_block.css('td[nowrap]::text').extract())
      enrollment_start_date = enrollment_dates[0] if len(enrollment_dates) == 2 else ''
      enrollment_end_date = enrollment_dates[1] if len(enrollment_dates) == 2 else ''

      sblock = blocks[1]
      group_name = sblock.css('td[width="32%"]::text').extract_first().strip()
      # Group has a teacher or it's empty eg. Ryhmä 99
      group_teacher = strip(sblock.css('td[width="32%"] a::text').extract_first())

      schedule_table = sblock.css('td[width="36%"] table[width="100%"]')
      # Schedule is inside this list as non-empty strings:
      # ['10.11.17', '', 'pe 10.15-12.00', '' ...]
      schedule_blocks = schedule_table.css('td::text').extract()
      # Classrooms are embedded inside inputs as values
      schedule_classrooms = schedule_table.css('input[type=SUBMIT] ::attr(value)').extract()
      # Language is in the last 'td' block as text
      tds = sblock.css('td')
      # IF len(tds) > 7
      if len(tds) > 7:
        languages = tds[len(tds) - 1].css('::text').extract()
        group_languages = strip(languages[1]) if len(languages) > 1 else ''
      else:
        group_languages = ''

      group_dict = {
        'enrolled': enrolled,
        'enrollment_max': enrollment_max,
        'enrollment_start_date': enrollment_start_date,
        'enrollment_end_date': enrollment_end_date,
        'group_name': group_name,
        'group_teacher': group_teacher,
        'schedule': [],
        'group_languages': group_languages
      }
      group_list.append(group_dict)

    return group_list