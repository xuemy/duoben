# encoidng:utf-8
from __future__ import unicode_literals
from app.models import Novel, FriendLink, Chapter, System
from django.http import Http404
from django.shortcuts import render, get_object_or_404

# Create your views here.

def index(request):
    system = System.objects.first()
    if not system:
        novel = Novel.objects.first()
    else:
        novel = system.index_novel

    chapters = novel.chapter_set.all()

    friendlinks = FriendLink.objects.all()
    hot_novels = Novel.objects.exclude(id=novel.id).order_by('-create_time').all()
    update_novels = Novel.objects.exclude(id=novel.id).order_by("-lastchaptertime").all()

    return render(request, "index.html", locals())


def novel(request, slug):
    novel = get_object_or_404(Novel, slug=slug)
    chapters = novel.chapter_set.all()
    hot_novels = Novel.objects.exclude(id=novel.id).order_by('-create_time').all()
    update_novels = Novel.objects.exclude(id=novel.id).order_by("-lastchaptertime").all()
    return render(request, "novel.html", locals())


def chapter(request, slug, cid):
    try:
        chapter = Chapter.objects.select_related("novel").get(id=cid)
        novel = chapter.novel
        hot_novels = Novel.objects.exclude(id=novel.id).order_by("-create_time")[:4]
    except:
        raise Http404()

    if novel.slug != str(slug):
        raise Http404()

    return render(request, "chapter.html", locals())