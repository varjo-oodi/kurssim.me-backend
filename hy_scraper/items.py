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
    opintoni_url = scrapy.Field()
    teachers = scrapy.Field()