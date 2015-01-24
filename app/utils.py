#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import json
from codemirror import CodeMirrorTextarea
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify

from django.utils.timezone import utc
from datetime import datetime
from jsonfield import JSONField
from jsonfield.forms import JSONFormField
from jsonfield.utils import default
import os, posixpath
from w3lib.util import unicode_to_str

now = lambda: datetime.utcnow().replace(tzinfo=utc)
sha1 = lambda x: hashlib.sha1(unicode_to_str(x)).hexdigest()


def img_key(instance, filename):
    return posixpath.join(
        "img", sha1(filename) + ".jpg"
    )


class MyFileStorage(FileSystemStorage):
    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, add an underscore and a random 7
        # character alphanumeric string (before the file extension, if one
        # exists) to the filename until the generated filename doesn't exist.
        while self.exists(name):
            self.delete(name)
            # file_ext includes the dot.
            # name = os.path.join(dir_name, "%s_%s%s" % (file_root, get_random_string(7), file_ext))

        return name


class JSONWidget(CodeMirrorTextarea):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        if not isinstance(value, basestring):
            value = json.dumps(value, indent=2, default=default)
        return super(JSONWidget, self).render(name, value, attrs)


class MyJSONField(JSONField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': JSONFormField,
            'widget': JSONWidget(mode="python", theme="cobalt", config={'fixedGutter': True})
        }
        defaults.update(**kwargs)
        return super(JSONField, self).formfield(**defaults)


if __name__ == "__main__":
    print now()

    print slugify("薛梦阳")