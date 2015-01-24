#!/usr/bin/python
# -*- coding: utf-8 -*-
from app.models import System


def process(request):
    system = System.objects.select_related("novel").first()

    return locals()