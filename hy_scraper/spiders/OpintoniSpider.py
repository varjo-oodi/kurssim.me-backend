import scrapy

from hy_scraper.items import CourseItem

def strip(text):
  if text: return text.strip()
  else: return ''

def strip_list(text):
  if text: return text.strip()
  else: return ''

# Eg. '\r\r10.10.17\r\n        klo 09.00-\r\r'
def strip_date(text):
  chunks = strip(text).split(' ')
  return strip(chunks[0])

# Eg. '\r\n                            30.10.2017 -19.11.2017\r\n                        '
# Or: '\r\n                            30.10.2017\r\n                        '
def strip_date_range(text):
  chunks = strip(text).split('-')
  if len(chunks) == 1:
    return [strip(chunks[0])]
  return [strip(chunks[0]), strip(chunks[1])]

# https://gist.github.com/douglasmiranda/2174255
def parseInt(string):
    return int(''.join([x for x in string if x.isdigit()]))

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
      course_dict['id'] = parseInt(url_chunks[len(url_chunks) - 1])
      # print(course_dict)
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
    credits = parseInt(info_trs[1].css('td')[1].css('::text').extract_first().strip())
    # 5 has the Date
    course_dates = strip_date_range(info_trs[3].css('td')[1].css('::text').extract_first())
    start_date = course_dates[0]
    end_date = course_dates[1] if len(course_dates) > 1 else ''
    print('credits: {} , date: {}'.format(credits, course_dates))

    group_table = response.css('table.kll')
    groups = self.scrape_oodi_groups(group_table)

    course['credits'] = credits
    course['start_date'] = start_date
    course['end_date'] = end_date
    print(groups)
    yield CourseItem(course)

  def scrape_oodi_groups(self, table):
    group_list = []
    groups = table.xpath('*')
    for i, group in enumerate(groups):
      # First element is just the header table
      if i == 0: continue
      blocks = group.xpath('*')
      first_block = blocks[0]
      # Containts enrolled/max as string '50/50'
      enrollment = first_block.css('td[width="14%"]::text').extract_first().strip()
      enrollment_chunks = enrollment.split('/')
      enrolled = enrollment_chunks[0]
      enrollment_max = enrollment_chunks[1]

      # Contains two strings with enrollment dates:
      # ['02.10.17\r\n        klo 09.00-', '15.12.17\r\n        klo 23.59']
      enrollment_date_blocks = first_block.css('td[nowrap]::text').extract()
      enrollment_start_date = strip_date(enrollment_date_blocks[0])
      enrollment_end_date = strip_date(enrollment_date_blocks[1])

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