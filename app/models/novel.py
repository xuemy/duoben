#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from crawl import Rule
from app.utils import MyFileStorage, img_key, sha1
from django.db import models
from django.db.models import permalink
from django.utils.text import slugify
import pypinyin
from w3lib.util import str_to_unicode


class Novel(models.Model):
    class Meta:
        verbose_name = '小说'
        verbose_name_plural = '小说'


    rule = models.ForeignKey(Rule)
    crawl_url = models.URLField("小说采集地址")
    name = models.CharField(max_length=50, unique=True, verbose_name="小说名")
    # TODO 修改save方法，slug 使用拼音代替
    slug = models.CharField(max_length=100, verbose_name="拼音", blank=True, null=True)
    author = models.CharField(max_length=100, db_index=True, verbose_name="作者", blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    # category = models.ForeignKey(Category, blank=True, null=True)
    intro = models.TextField(verbose_name="小说简介", blank=True, null=True)
    img = models.ImageField(upload_to=img_key, storage=MyFileStorage(), blank=True, null=True)
    hash = models.CharField(unique=True, max_length=40, blank=True, null=True)

    lastchapterid = models.IntegerField(blank=True, null=True)
    lastchaptername = models.CharField(max_length=200, verbose_name="最新章节名", blank=True, null=True)
    lastchaptertime = models.DateTimeField(blank=True, null=True)

    seo_title = models.TextField("seo标题", blank=True, null=True)
    seo_keywords = models.TextField("seo关键字", blank=True, null=True)
    seo_description = models.TextField("seo描述", blank=True, null=True)

    create_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = pypinyin.slug(str_to_unicode(self.name), separator=u"")
        if not self.hash:
            self.hash = sha1(self.name)
        models.Model.save(self)

    def __unicode__(self):
        return self.name

    @property
    def get_img_url(self):
        if self.img:
            return self.img.url
        else:
            return "http://xiaoshuo-img.qiniudn.com/nocover.jpg"

    @permalink
    def get_lastchapter_url(self):

        if self.lastchapterid:
            return ("chapter", [self.slug, self.lastchapterid])
        else:
            return ("novel", [self.slug])

    @permalink
    def get_novel_url(self):
        from system import System

        system = System.objects.select_related("novel").first()
        index_novel = system.index_novel
        if index_novel.id == self.id:
            return ("index", [])
        else:
            return ("novel", [self.slug])