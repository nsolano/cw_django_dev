# tests.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question

class QuestionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title='Test Question', description='This is a test question', author=self.user)
    
    def tearDown(self):
        self.user.delete()
        self.question.delete()

    def test_question_model(self):
        self.assertEqual(str(self.question.title), 'Test Question')

    def test_question_list_view(self):
        login_successful = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_successful)

        response = self.client.get(reverse('survey:question-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Question')
