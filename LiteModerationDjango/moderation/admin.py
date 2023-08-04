from django.contrib import admin
from django.db import models
from django import forms
from django.utils.text import Truncator

from moderation.models import Specialty, Doctor, Review, ObsceneWord, ExceptionWord


@admin.register(ObsceneWord)
class ObsceneAdmin(admin.ModelAdmin):
    search_fields = ('word',)


@admin.register(ExceptionWord)
class ExceptionWordAdmin(admin.ModelAdmin):
    search_fields = ('word',)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    search_fields = ('id', 'last_name', 'second_name', 'name', 'specialties__name')
    list_display = ('id', 'last_name', 'second_name', 'name', 'all_specialties')
    list_display_links = ('id', 'last_name', 'second_name', 'name')
    list_filter = ('id', 'last_name', 'second_name', 'name', 'specialties')

    def all_specialties(self, obj):
        return "\n".join([str(name) for name in obj.specialties.all()])

    all_specialties.short_description = 'Специальности'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    empty_value_display = 'Аноним'
    list_per_page = 100
    list_display = ('id', 'doctor', 'user', 'short_original_text', 'short_processed_text', 'ip_address')
    list_display_links = ('id', 'doctor', 'user')

    list_filter = ('doctor', 'date', 'user', 'ip_address')
    readonly_fields = ('date', 'original_text')
    search_fields = (
        'id', 'user__username', 'doctor__name', 'doctor__last_name', 'doctor__second_name', 'original_text',
        'processed_text', 'ip_address')
    raw_id_fields = ("doctor", "user")

    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'rows': 10, 'cols': 160})}
    }

    def short_original_text(self, obj):
        return Truncator(obj.original_text).chars(49, truncate="...")

    def short_processed_text(self, obj):
        return Truncator(obj.processed_text).chars(49, truncate="...")

    short_original_text.short_description = 'Исходный текст отзыва'
    short_processed_text.short_description = 'Текст отзыва после проверки'
