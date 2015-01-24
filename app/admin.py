from app.models import Rule, Novel, Crawl, Chapter, Category, System
from django.contrib import admin

# Register your models here.


admin.site.register(Rule)
admin.site.register(Novel)
admin.site.register(Category)
admin.site.register(Chapter)
admin.site.register(Crawl)
admin.site.register(System)