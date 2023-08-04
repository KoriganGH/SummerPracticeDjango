from django.db.models.signals import pre_save
from django.contrib import messages
from .models import Doctor
from .forms import ReviewForm
# from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from .models import Review, ObsceneWord, ExceptionWord
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.contrib.auth.models import User, AnonymousUser
from functools import wraps
from django.db import connection


# Встроенный декоратор мне не подошел
def staff_member_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        return func(request, *args, **kwargs)

    return wrapper


@staff_member_required
def review_list(request):
    reviews = Review.objects.all().select_related('doctor').prefetch_related('doctor__specialties')

    obscene_words = ObsceneWord.objects.values_list('word', flat=True)
    exception_words = ExceptionWord.objects.values_list('word', flat=True)
    context = {
        'reviews': reviews,
        'obscene_words': obscene_words,
        'exception_words': exception_words,
    }

    return render(request, 'review_list.html', context)


def add_review(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    specialties = ', '.join([str(specialty) for specialty in doctor.specialties.all()])
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            if request.user != AnonymousUser():
                review.user = request.user
            review.doctor = doctor
            review.add_new_lines_in_text()
            review.processed_text = review.text_formatting()
            request.review = review  # Добавляем отзыв к объекту запроса
            pre_save.send(sender=Review, instance=review, request=request)  # Отправляем сигнал pre_save
            review.save()
            # messages.success(request, 'Получен новый отзыв')
            return redirect('success')
    else:
        form = ReviewForm()

    return render(request, 'add_review.html', {'form': form, 'doctor': doctor, 'specialties': specialties})


def success(request):
    return render(request, 'success.html')
