#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tempfile
from StringIO import StringIO

from PIL import Image
from app.models import Novel, Crawl, Chapter
from app.utils import sha1
from crawl.utils import Filter
from django.core.files import File
from scrapy import Spider, Selector, Request, log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url
from six import moves

from crawl.items import NovelLoader, ChapterLoader


class One(Spider):
    name = "single_crawl"

    def __init__(self, *args, **kwargs):
        super(One, self).__init__(*args, **kwargs)
        all_novel = Novel.objects.all()
        self.crawl_dict = {sha1(novel.crawl_url): novel for novel in all_novel}

        self.start_urls = [novel.crawl_url for novel in all_novel]

    def parse_img(self, response):
        novel_id = response.meta.get("novel_id")
        novel = Novel.objects.get(id=novel_id)
        body = response.body
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
        self.log("图片保存成功，%s" % novel.img.url)

    def parse(self, response):
        url = response.url
        novel = self.crawl_dict.get(sha1(url))
        rule = novel.rule

        config = rule.rule

        sel = Selector(response=response)
        novel_item = NovelLoader(selector=sel)

        # 获取小说信息
        novel_item.add_xpath("name", config.get("NovelName_XPATH"), re=config.get("NovelName_RE", None))
        novel_item.add_xpath("intro", config.get("NovelIntro_XPATH"), re=None)
        novel_item.add_xpath("author", config.get("NovelAuthor_XPATH"), re=config.get("NovelAuthor_RE", None))
        novel_item.add_xpath("category", config.get("NovelCategory_XPATH"), re=config.get("NovelCategory_RE", None))
        novel_img = "".join(sel.xpath(config.get("NovelImg_XPATH")).extract())

        if "http://" not in novel_img:
            base_url = get_base_url(response)
            novel_img = moves.urllib.parse.urljoin(base_url, novel_img)

        _novel_item = novel_item.load_item()

        # 获取或创建小说
        _category = _novel_item.get("category")

        if not novel.category:
            novel.category = _category
        if not novel.author:
            novel.author = _novel_item.get("author")
        if not novel.intro:
            novel.intro = _novel_item.get("intro")

        novel.save()

        if not novel.img:
            self.log("小说<%s>封面图片没有下载，提交到图片下载队列" % novel.name, level=log.INFO)
            yield Request(url=novel_img, callback=self.parse_img, meta=dict(novel_id=novel.id))

        # 假如小说详情和章节列表不在同一个页面，进行一个判断
        if config.get("ChapterList_Flag", None):
            self.log("小说<%s>详情页和章节列表页不在同一页面，获取小说章节页" % novel.name, level=log.INFO)

            chapter_url = "".join(sel.xpath(config.get("ChapterList_URL")).extract()).strip()

            # 获取正确的 chapter_url
            if "http://" not in chapter_url:
                base_url = get_base_url(response)
                chapter_url = moves.urllib.parse.urljoin(base_url, chapter_url)

            yield Request(url=chapter_url, callback=self.chapterlist_parse,
                          meta={"novel_id": novel.id, "config": config})
        else:
            # 获取小说章节列表
            self.log("小说<%s>详情页和章节列表页在同一页面,正在获取获取小说章节" % novel.name, level=log.INFO)
            novel_chapterlists = SgmlLinkExtractor(
                restrict_xpaths=(config.get("NovelChapterList_XPATH"),),
            ).extract_links(response)

            for num, chapter in enumerate(novel_chapterlists, start=1):
                c = Chapter.objects.filter(hash=sha1(chapter.url)).first()
                if not c:
                    self.log("添加%s-%s" % (novel.name, chapter.text), level=log.DEBUG)
                    yield Request(url=chapter.url,
                                  callback=self.chapter_parse,
                                  meta=dict(sort=unicode(num), chapter_name=chapter.text, novel_id=novel.id,
                                            config=config))
                else:
                    pass
                    # print c.name

    def chapterlist_parse(self, response):
        self.log("获取小说章节列表url")
        config = response.meta['config']
        novel_chapterlists = SgmlLinkExtractor(
            restrict_xpaths=(config.get("NovelChapterList_XPATH"),),
        ).extract_links(response)

        novel_id = response.meta['novel_id']

        for num, chapter in enumerate(novel_chapterlists, start=1):
            c = Chapter.objects.filter(hash=sha1(chapter.url)).first()
            if not c:
                self.log("章节不在数据库，提交到下载列表", level=log.DEBUG)
                yield Request(url=chapter.url,
                              callback=self.chapter_parse,
                              meta=dict(sort=unicode(num), chapter_name=chapter.text, novel_id=novel_id, config=config))

    def chapter_parse(self, response):
        sel = Selector(response)
        config = response.meta['config']
        content = sel.xpath(config.get("ChapterContent_XPATH")).extract()
        chapter_item = ChapterLoader(selector=sel)
        novel_id = response.meta.get("novel_id")
        novel = Novel.objects.get(id=novel_id)
        chapter_item.add_value("name", response.meta.get("chapter_name"), Filter(config.get("filters")))
        chapter_item.add_value("sort", response.meta.get("sort"))
        chapter_item.add_value("content", content, Filter(config.get("filters"), config.get("regex")))
        chapter_item.add_value("novel", novel_id)
        chapter_item.add_value("hash", sha1(response.url))
        # chapter_item.add_value("intro", "".join(content)[:300], Filter(config.get("filters")))
        _chapter = chapter_item.load_item()

        self.log("小说《%s》最新章节%s章节下载成功，提交到保存队列" % (novel.name, _chapter['name']), level=log.DEBUG)
        # 对于图片章节，先进行跳过处理
        # if _chapter['content'] or _chapter['content'].strip() == "":
        yield _chapter

