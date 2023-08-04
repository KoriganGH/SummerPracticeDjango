from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
import re


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'


class Doctor(models.Model):
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    name = models.CharField(max_length=100, verbose_name='Имя')
    second_name = models.CharField(max_length=100, verbose_name='Отчество')

    specialties = models.ManyToManyField(Specialty, related_name='doctors', verbose_name="Специальности")

    @property
    def full_name(self):
        return f"{self.last_name} {self.name} {self.second_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Доктор'
        verbose_name_plural = 'Доктора'


class ObsceneWord(models.Model):
    word = models.CharField(max_length=100, unique=True, verbose_name='Слово')

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = 'Оскорбительное слово'
        verbose_name_plural = 'Оскорбительные слова'


class ExceptionWord(models.Model):
    word = models.CharField(max_length=100, unique=True, verbose_name='Слово')

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = 'Слово-исключение'
        verbose_name_plural = 'Слова-исключения'


class Review(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='reviews',
                               on_delete=models.CASCADE, verbose_name='Доктор')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    original_text = models.CharField(validators=[MinLengthValidator(100, message='Должно быть хотя бы 100 символов')],
                                     max_length=2000, verbose_name='Исходный текст отзыва')

    processed_text = models.CharField(validators=[MinLengthValidator(100, message='Должно быть хотя бы 100 символов')],
                                      max_length=2000, verbose_name='Текст отзыва после проверки')

    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP-адрес')
    user = models.ForeignKey(User, related_name='reviews',
                             on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')

    def __str__(self):
        return f"Отзыв номер {self.id}"

    # Опциональный метод для добавления \n, после 150 символов (нужно доработать)
    def add_new_lines_in_text(self):
        self.original_text = re.sub("(.{150})", "\\1\n", self.original_text, 0, re.DOTALL)
        #self.original_text = re.sub(r'(.{150}(?<!\n))(?!$)','\1\n\n',self.original_text)

    def text_formatting(self):
        preprocessed_text = re.sub(r'\b([A-ZА-ЯЁ]{6,})\b', lambda match: match.group(1).lower(), self.original_text)
        preprocessed_text = re.sub(r"([.?!]\s*)(\w)", lambda m: m.group(1) + m.group(2).capitalize(), preprocessed_text)
        preprocessed_text = re.sub(r"(\W)\1+", r"\1", preprocessed_text)
        preprocessed_text = re.sub(r"\s*([^\w\s])\s*", r"\1 ", preprocessed_text)
        self.processed_text = (preprocessed_text[0].upper() + preprocessed_text[1:]).rstrip()
        return self.processed_text

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


# Хук для получения ip адреса
@receiver(pre_save, sender=Review)
def set_review_ip_address(sender, instance, **kwargs):
    request = kwargs.get('request')
    if request and not instance.ip_address:
        instance.ip_address = get_client_ip(request)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
