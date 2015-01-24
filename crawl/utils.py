#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.etree import ElementTree
import six
import re
from django.utils.encoding import smart_unicode

_regex_url = re.compile(
    ur"(http(s)?://.)?(www\.)?[-a-zA-Z0-9@:!$^&\*%.()_\+~#=\uff10-\uff40{}\[\]]{2,256}[\[\]{}!$^\*&@:%._\+~#-=()][\[\]{}a-z!$^\*&@:%._\uff10-\uff40\s]{2,6}\b([\[\]-a-zA-Z0-9()@:%_\+.~#?&//=]*)")


def split_text(s, flag="`"):
    if isinstance(s, six.string_types) and flag in s:
        return [ss.strip() for ss in s.split(flag)]
    else:
        return s


def parse_xml(xml_path):
    tree = ElementTree.parse(xml_path)
    root = tree.getroot()
    result = dict()
    for sub in root:
        result[sub] = dict([(t.tag, split_text(t.text)) for t in sub])
    return result


class Filter(object):
    def __init__(self, f="", regex=""):
        if not f:
            f = ""
        self.filters = f.split("|")
        _regex = regex if regex else ""
        self._regex = smart_unicode(_regex)

    def __call__(self, content):
        # 去除网页中的url
        content = map(lambda c: _regex_url.sub(u"", c), content)
        # 使用正则去除网页中的其他垃圾内容
        content = map(lambda c: re.sub(self._regex, u"", c), content)

        for filter in self.filters:
            content = map(
                lambda s: s.replace(smart_unicode(filter), u""), content)
        return content

    def remove_url(self, content):
        return _regex_url.sub(u"", content)

    def custom_regex(self, content):
        return re.sub(self._regex, u"", content)
