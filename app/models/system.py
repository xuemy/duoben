#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from app.models.novel import Novel
from django.db import models

# Create your models here.
from django.db.models import permalink


class System(models.Model):
    class Meta:
        verbose_name = '系统设置'
        verbose_name_plural = '系统设置'

    name = models.CharField("站点名", max_length=100)
    domain = models.URLField("站点域名", max_length=255)
    index_novel = models.ForeignKey(Novel, blank=True, verbose_name="首页主推小说", null=True)

    global_title_t = models.TextField("首页seo标题模板", blank=True, null=True)
    global_keys_t = models.TextField("首页keys模板", blank=True, null=True)
    global_desc_t = models.TextField("首页description模板", blank=True, null=True)

    tongji = models.TextField("统计代码", blank=True, null=True)
    # sousuo = models.TextField("搜索代码", blank=True, null=True)

    ad = models.TextField("广告代码", blank=True, null=True)

    def __unicode__(self):
        return self.name

    @permalink
    def get_system_url(self):
        return ("index", [])


class FriendLink(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=255)

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = '友情链接'

    def __unicode__(self):
        return self.name