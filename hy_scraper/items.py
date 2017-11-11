# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CourseItem(scrapy.Item):
    id = scrapy.Field()
    tag = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    format = scrapy.Field()
    study_field = scrapy.Field()
    credits = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    enrollment_start_date = scrapy.Field()
    enrollment_end_date = scrapy.Field()

    opintoni_url = scrapy.Field()
    oodi_url = scrapy.Field()
    teachers = scrapy.Field()

    groups = scrapy.Field()

    # short_description = scrapy.Field()
    # schedule = scrapy.Field() # List of locations of lectures etc.
    # description = scrapy.Field() # Long block of text in most cases