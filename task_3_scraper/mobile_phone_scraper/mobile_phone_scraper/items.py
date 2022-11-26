# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MobilePhoneScraperItem(scrapy.Item):
    operating_system_version = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
