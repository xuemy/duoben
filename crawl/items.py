# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Compose, Join, TakeFirst


class MengItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NovelItem(scrapy.Item):
    name = scrapy.Field()
    author = scrapy.Field()
    category = scrapy.Field()
    intro = scrapy.Field()


class ChapterItem(scrapy.Item):
    name = scrapy.Field()
    content = scrapy.Field()
    sort = scrapy.Field()
    novel = scrapy.Field()
    hash = scrapy.Field()
    # intro = scrapy.Field()


class BookImage(scrapy.Item):
    novel_id = scrapy.Field()
    img_url = scrapy.Field()
    content = scrapy.Field()


class NovelLoader(ItemLoader):
    default_item_class = NovelItem

    default_output_processor = Compose(Join(""), unicode.strip)


class ChapterLoader(ItemLoader):
    default_item_class = ChapterItem
    default_output_processor = Compose(Join(""), unicode.strip)

    novel_out = TakeFirst()
    content_out = Compose(lambda c: ['<p>%s</p>' % cc for cc in c], Join(""), unicode.strip)
    hash_out = Join("")
    intro_out = Join("")
