#!/usr/bin/python
# -*- coding: utf-8 -*-
from pprint import pprint
from UserDict import UserDict

from xml.etree import ElementTree

tree = ElementTree.parse("23us.xml")

root = tree.getroot()

s = UserDict()


# for c in root:
# _s = dict()
# for sc in c:
#         _s[sc.tag] = sc.text
#     s[c.tag] = _s
# print s

def split_text(s):
    if not s:
        return s
    if "," not in s:
        return s
    return [_s.strip() for _s in s.split(",")]


for c in root:
    d = dict([(sc.tag, split_text(sc.text)) for sc in c])
    s[c.tag] = d

pprint(s)
