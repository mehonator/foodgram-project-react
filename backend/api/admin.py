from django.contrib import admin
from api.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

