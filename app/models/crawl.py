#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from app.utils import MyJSONField


class Rule(models.Model):
    class Meta:
        verbose_name = '采集规则'
        verbose_name_plural = '采集规则'

    name = models.CharField("采集名", max_length=100)
    rule = MyJSONField("采集规则")

    def __unicode__(self):
        return self.name


class Crawl(models.Model):
    url = MyJSONField("采集地址")
    rule = models.ForeignKey(Rule)

    def __unicode__(self):
        return self.id