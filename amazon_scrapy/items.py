# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Marketplace_Name = scrapy.Field()
    ASIN = scrapy.Field()
    url = scrapy.Field()
    lower_frame = scrapy.Field()
    comment_num = scrapy.Field()
    stars = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    dimensions = scrapy.Field()
    productWeight = scrapy.Field()
    shippingWeight = scrapy.Field()
    is_404 = scrapy.Field()
    is_robot = scrapy.Field()
    pass
