# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import scrapy
from hy_scraper.items import CourseItem

class CourseJsonPipeline(object):
    def open_spider(self, spider):
        os.makedirs('output', exist_ok=True)
        self.file_courses = open('output/hy_courses.json', 'w')

    def close_spider(self, spider):
        self.file_courses.close()

    def process_item(self, item, spider):
        if isinstance(item, CourseItem):
            print(dict(item))
            line = json.dumps(dict(item)) + "\n"
            self.file_courses.write(line)