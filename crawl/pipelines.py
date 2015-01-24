# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# import os,sys
# import django
#
from __future__ import unicode_literals
from datetime import datetime
from app.models import Novel, Chapter
from app.utils import now
from django.utils.timezone import utc
import os
import sys
import tempfile
from StringIO import StringIO

from PIL import Image
import django
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from scrapy import log
import w3lib.html


current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'shu.settings'
django.setup()
from crawl.items import BookImage


class MengPipeline(object):
    def process_item(self, item, spider):
        novel_id = item['novel']
        novel = Novel.objects.get(id=novel_id)
        chapter = Chapter(
            novel=novel,
            name=item['name'],
            sort=item['sort'],
            content=item['content'],
            hash=item['hash'],
            # intro=w3lib.html.remove_tags(item['content'][:300]),
            create_time=now()
        )

        novel.lastchaptername = chapter.name
        novel.lastchaptertime = now()
        try:
            chapter.save()
            novel.lastchapterid = chapter.id
            novel.save()
            log.msg("小说《%s》最新章节%s保存到数据库成功 ID:%s" % (novel.name, item['name'], str(chapter.id)))
        except Exception, err:
            print err


class ImgPieline(object):
    def process_item(self, item, spider):
        if isinstance(item, BookImage):
            log.msg("img instance")
            novel = Novel.objects.get(id=item['novel_id'])
            body = item['content']
            img_url = item['img_url']
            orig_image = Image.open(StringIO(body))

            def convert_image(image):
                if image.format == 'PNG' and image.mode == 'RGBA':
                    background = Image.new('RGBA', image.size, (255, 255, 255))
                    background.paste(image, image)
                    image = background.convert('RGB')
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                temp = tempfile.NamedTemporaryFile(suffix=".jpg")
                image.save(temp, 'JPEG')
                return image, temp

            image, temp = convert_image(orig_image)

            novel.img = File(temp)
            novel.save()
            temp.close()
        else:
            print type(item)
            print type(BookImage())
            print type(item) == type(BookImage())

            log.msg("not img instance")
        return item