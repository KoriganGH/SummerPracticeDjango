from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from django.shortcuts import reverse
from .models import Doctor, Review, ObsceneWord, ExceptionWord, set_review_ip_address
from .views import review_list, add_review, success
from .forms import ReviewForm
from .factories import ReviewFactory, DoctorFactory


class ReviewTestCase(TestCase):

    def test_format_text(self):
        input_texts = ['Красный , белый , синий - это всё цвета ', 'ПОГОДА СЕГОДНЯ ХОРОШАЯ!!!!!!',
                       'ПРИВЕТ. ПРИВЕТ ТЕСТ',
                       'это все конечно очень хорошо , но я не понимаю . как же - ЭТОООО работает? да я и сам не знаю.',
                       'АБВ ГД абвгде ТЕСТТЕСТ ТЕСТЫ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',
                       'ААААА', 'ББББББ']

        expected_texts = ['Красный, белый, синий- это всё цвета', "Погода сегодня хорошая!", 'Привет. Привет ТЕСТ',
                          'Это все конечно очень хорошо, но я не понимаю. Как же- этоооо работает? Да я и сам не знаю.',
                          'АБВ ГД абвгде тесттест ТЕСТЫ!', 'ААААА', 'Бббббб']

        doctor = Doctor.objects.create()

        for index, input_text in enumerate(input_texts):
            with self.subTest(input_text=input_text):
                review = Review.objects.create(doctor=doctor, original_text=input_text)
                formatted_text = review.text_formatting()
                expected_answer = expected_texts[index]

                self.assertEqual(expected_answer, formatted_text)


class ReviewListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='admin', is_staff=True)
        self.review = ReviewFactory()

    def test_review_list_view_with_staff_user(self):
        request = self.factory.get(reverse('review_list'))
        request.user = self.user

        response = review_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.review.doctor.full_name)

    def test_review_list_view_with_non_staff_user(self):
        request = self.factory.get(reverse('review_list'))
        request.user = User.objects.create(username='user')

        with self.assertRaises(Http404):
            review_list(request)


class AddReviewViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.doctor = DoctorFactory()
        self.user = User.objects.create(username='admin', is_staff=True)

    def test_add_review_view_get(self):
        request = self.factory.get(reverse('add_review', args=[self.doctor.id]))
        request.user = self.user

        response = add_review(request, self.doctor.id)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.doctor.full_name)

    def test_add_review_view_post_with_authenticated_user(self):
        request = self.factory.post(reverse('add_review', args=[self.doctor.id]), {
            'original_text': 'Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test'
                             'Test Test Test Test Test Test Test TestTest Test Test Test Test Test Test Test',
        })
        request.user = self.user

        response = add_review(request, self.doctor.id)

        review = Review.objects.get(doctor=self.doctor)
        self.assertEqual(review.ip_address, '127.0.0.1')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('success'))

    def test_add_review_view_post_with_anonymous_user(self):
        request = self.factory.post(reverse('add_review', args=[self.doctor.id]), {
            'original_text': 'Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test'
                             'Test Test Test Test Test Test Test TestTest Test Test Test Test Test Test Test',
        })
        request.user = AnonymousUser()
        response = add_review(request, self.doctor.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('success'))


class SuccessViewTest(TestCase):
    def test_success_view(self):
        response = self.client.get(reverse('success'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'success.html')

