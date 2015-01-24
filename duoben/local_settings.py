#!/usr/bin/python
# -*- coding: utf-8 -*-
from app import admin
from django.conf.urls import patterns, url, include

DB_NAME = "duoben"
DB_USER = "duoben"
DB_PASSWORD = "xmy@5650268"
DEBUG = True

local_url = patterns("",url(r'^xmy/admin/', include(admin.site.urls)),)