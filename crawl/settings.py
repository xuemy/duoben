# -*- coding: utf-8 -*-

# Scrapy settings for meng project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#
from __future__ import unicode_literals
import os, sys
import django

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'duoben.settings'
django.setup()
BOT_NAME = '小说采集'

SPIDER_MODULES = ['crawl.spider']
NEWSPIDER_MODULE = 'crawl.spider'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = '"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0"'

# 同时下载个数
CONCURRENT_REQUESTS = 5
CONCURRENT_REQUESTS_PER_SPIDER = 5
CLOSESPIDER_PAGECOUNT = 100000
CLOSESPIDER_TIMEOUT = 36000
DOWNLOAD_DELAY = 1.5  # 1000ms
# RANDOMIZE_DOWNLOAD_DELAY = True
RETRY_ENABLED = False
COOKIES_ENABLED = False

DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'


# Don't cleanup redis queues, allows to pause/resume crawls.
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# SCHEDULER_PERSIST = False
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'

# Schedule requests using a priority queue. (default)
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

# Schedule requests using a queue (FIFO).

# Schedule requests using a stack (LIFO).
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderStack'




ITEM_PIPELINES = {
    "pipelines.MengPipeline": 800,
    # "pipelines.ImgPieline": 800,

}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'middlewares.RotateUserAgentMiddleware': 400,
}

LOG_LEVEL = "INFO"

RULE = ""