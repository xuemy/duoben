# encoding:utf-8
from collections import defaultdict

from django.http import HttpResponseNotFound
from django.template import loader
from django.template import RequestContext


def render_to_not_found(*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'content_type': kwargs.pop('content_type', None)}

    return HttpResponseNotFound(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)

def not_found(request):
    from app.models import Novel
    result = defaultdict()
    random_novels = Novel.objects.order_by("?")[:20]
    result['novels'] = random_novels
    return render_to_not_found("not_found.html",result,context_instance=RequestContext(request))

