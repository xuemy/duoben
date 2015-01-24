#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from app.models.novel import Novel
from django.db import models
from django.db.models import permalink


class Chapter(models.Model):
    class Meta:
        verbose_name = '章节'
        verbose_name_plural = '章节'
        index_together = [['sort', "novel"], ["novel", "create_time"]]

    novel = models.ForeignKey(Novel)
    name = models.CharField(max_length=200, verbose_name="章节名")
    sort = models.IntegerField(db_index=True, verbose_name="章节序号")
    content = models.TextField("章节内容")
    hash = models.CharField(max_length=40, unique=True)

    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    @permalink
    def get_chapter_url(self):

        return ("chapter", [self.novel.slug, self.id])

    @property
    def get_pre_chapter(self):
        try:
            chapter = Chapter.objects.filter(novel=self.novel, sort__lt=self.sort).latest('sort')
            return chapter.get_chapter_url
        except:
            return self.novel.get_novel_url

    @property
    def get_next_chapter(self):
        try:
            chapter = Chapter.objects.filter(novel=self.novel, sort__gt=self.sort).earliest('sort')
            return chapter.get_chapter_url
        except:
            return self.novel.get_absolute_url