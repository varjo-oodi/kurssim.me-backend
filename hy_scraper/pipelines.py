# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import scrapy
from scrapy.exporters import JsonItemExporter
from hy_scraper.items import CourseItem

class CourseJsonPipeline(object):
    def open_spider(self, spider):
        self.file_courses = open("output/hy_courses.json", 'wb')
        self.exporter = JsonItemExporter(self.file_courses, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file_courses.close()
 
    def process_item(self, item, spider):
        if isinstance(item, CourseItem):
            print(dict(item))
            self.exporter.export_item(item)
        return item