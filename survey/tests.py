"""
Módulo de pruebas para la aplicación de raking de preguntas.

Este módulo contiene varias clases de pruebas que evalúan diferentes aspectos
de la. Cada clase de prueba se enfoca en un componente o
funcionalidad específica de la aplicación.

Estructura General:
- `QuestionTestCase`: Pruebas para el modelo de preguntas.
- `AnswerTestCase`: Pruebas para el modelo de respuestas a preguntas.
- `QuestionFeedbackTestCase`: Pruebas para el modelo de retroalimentación de preguntas.
- `QuestionManagerTestCase`: Pruebas para el administrador de preguntas.
- `QuestionListViewTest`: Pruebas para la vista de lista de preguntas.
- `AnswerQuestionErrorTestCase`: Pruebas para el manejo de errores al responder preguntas.
- `LikeDislikeQuestionErrorTestCase`: Pruebas para el manejo de errores al votar por preguntas.

Cada clase de prueba contiene métodos específicos que cubren casos de uso y escenarios
particulares relacionados con la funcionalidad que están evaluando. Las pruebas se enfocan
tanto en la lógica del modelo como en la interacción con las vistas.
"""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Answer, Question, QuestionFeedback
from .views import QuestionManager


class QuestionTestCase(TestCase):
    """
    Clase de pruebas para el modelo `Question` y la vista `question-list`.

    Métodos de prueba:
    - `test_question_model`: Verifica la creación y representación de la pregunta en el modelo.
    - `test_question_list_view`: Verifica el comportamiento de la vista de lista de preguntas.
    """

    def setUp(self):
        """
        Configuración inicial para cada prueba.
        """
        # Crea un usuario de prueba
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Crea una pregunta de prueba
        self.question = Question.objects.create(
            title="Test Question",
            description="This is a test question",
            author=self.user,
        )

    def tearDown(self):
        # Elimina las instancias
        self.user.delete()
        self.question.delete()

    def test_question_model(self):
        # Verifica la creación de la pregunta
        self.assertEqual(str(self.question.title), "Test Question")

    def test_question_list_view(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Hace una solicitud GET a la vista con autenticación
        response = self.client.get(reverse("survey:question-list"))

        # Verifica que la solicitud sea satisfactoria
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Question")


class AnswerTestCase(TestCase):
    """
    Clase de pruebas para el modelo `Answer` y la vista `question-answer`.

    Métodos de prueba:
    - `test_answer_model`: Verifica la creación y representación de la respuesta en el modelo.
    - `test_answer_question_view`: Verifica el comportamiento de la vista de respuesta a una pregunta.
    """

    def setUp(self):
        # Crea un usuario de prueba
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Crea una pregunta y respuesta de prueba
        self.question = Question.objects.create(
            title="Test Question",
            description="This is a test question",
            author=self.user,
        )
        self.answer = Answer.objects.create(
            question=self.question,
            author=self.user,
            value=5,
            comment="This is a test comment",
        )

    def tearDown(self):
        # Elimina las instancias
        self.user.delete()
        self.question.delete()
        self.answer.delete()

    def test_answer_model(self):
        # Verifica la creación de la respuesta
        self.assertEqual(self.answer.value, 5)
        self.assertEqual(self.answer.comment, "This is a test comment")

    def test_answer_question_view(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Hace una solicitud POST a la vista con autenticación
        response = self.client.post(
            reverse("survey:question-answer"),
            {"question_pk": self.question.pk, "value": 4},
        )

        # Verifica que la solicitud sea satisfactoria
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Answer.objects.filter(question=self.question, author=self.user).count(), 1
        )


class QuestionFeedbackTestCase(TestCase):
    """
    Clase de pruebas para el modelo `QuestionFeedback` y la vista `question-like`.

    Métodos de prueba:
    - `test_feedback_model`: Verifica la creación y representación del feedback en el modelo.
    - `test_like_dislike_question_view`: Verifica el comportamiento de la vista de "like" o "dislike" a una pregunta.
    """

    def setUp(self):
        # Crea un usuario de prueba
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Crea una pregunta y feedback de prueba
        self.question = Question.objects.create(
            title="Test Question",
            description="This is a test question",
            author=self.user,
        )
        self.feedback = QuestionFeedback.objects.create(
            question=self.question, author=self.user, value="Like"
        )

    def tearDown(self):
        # Elimina las instancias
        self.user.delete()
        self.question.delete()
        self.feedback.delete()

    def test_feedback_model(self):
        # Verifica la creación del feedback
        self.assertEqual(self.feedback.value, "Like")

    def test_like_dislike_question_view(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Hace una solicitud POST a la vista con autenticación
        response = self.client.post(
            reverse("survey:question-like"),
            {"question_pk": self.question.pk, "value": "dislike"},
        )

        # Verifica que la solicitud sea satisfactoria
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            QuestionFeedback.objects.filter(
                question=self.question, author=self.user
            ).count(),
            1,
        )


class QuestionManagerTestCase(TestCase):
    """
    Clase de pruebas para el gestor de preguntas (`QuestionManager`).

    Esta clase de pruebas configura instancias de usuarios, preguntas, respuestas
    y feedbacks de prueba para evaluar el comportamiento del gestor de preguntas.

    Métodos de prueba específicos se encargan de verificar diversos aspectos
    relacionados con el cálculo de rankings, obtención de preguntas ordenadas y
    serialización de preguntas.

    Métodos de prueba:
    - `test_calculate_ranking`: Verifica que el cálculo del ranking sea correcto.
    - `test_get_ranked_questions`: Verifica que las preguntas se obtengan ordenadas por ranking.
    - `test_get_serialized_questions`: Verifica la correcta serialización de las preguntas.
    """

    def setUp(self):
        # Crea usuarios de prueba
        self.user1 = User.objects.create_user(
            username="testuser 1", password="testpass1"
        )
        self.user2 = User.objects.create_user(
            username="testuser 2", password="testpass2"
        )
        self.user3 = User.objects.create_user(
            username="testuser 3", password="testpass3"
        )

        # Crea preguntas de prueba
        self.question1 = Question.objects.create(
            title="Question 1",
            description="Description 1",
            author=self.user1,
            created=timezone.now(),
        )
        self.question2 = Question.objects.create(
            title="Question 2",
            description="Description 2",
            author=self.user2,
            created=timezone.now(),
        )
        self.question3 = Question.objects.create(
            title="Question 3",
            description="Description 3",
            author=self.user3,
            created=timezone.now(),
        )

        # Crea respuestas y feedbacks de prueba
        self.feedback1 = QuestionFeedback.objects.create(
            question=self.question1, author=self.user2, value="like"
        )
        self.feedback2 = QuestionFeedback.objects.create(
            question=self.question1, author=self.user3, value="dislike"
        )
        self.feedback3 = QuestionFeedback.objects.create(
            question=self.question3, author=self.user1, value="dislike"
        )
        self.answer1 = Answer.objects.create(
            question=self.question1, author=self.user2, value=4
        )
        self.answer2 = Answer.objects.create(
            question=self.question1, author=self.user3, value=1
        )

    def tearDown(self):
        # Elimina las instancias
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()

        self.question1.delete()
        self.question2.delete()
        self.question3.delete()

        self.feedback1.delete()
        self.feedback2.delete()
        self.feedback3.delete()

        self.answer1.delete()
        self.answer2.delete()

    def test_calculate_ranking(self):
        # Calcula el ranking
        ranking_calculated = QuestionManager.calculate_ranking(self.question1)

        # Calcula el ranking esperado
        answers = 2 * 10
        likes = 1 * 5
        dislikes = 1 * 3
        created_now = 10

        ranking_expected = answers + likes - dislikes + created_now

        # Verifica que el ranking se haya calculado correctamente
        self.assertEqual(ranking_calculated, ranking_expected)

    @patch("survey.views.Question.objects.all")
    def test_get_ranked_questions(self, mock_question_objects_all):
        # Calcula el ranking para cada pregunta
        QuestionManager.calculate_ranking(self.question1)
        QuestionManager.calculate_ranking(self.question2)
        QuestionManager.calculate_ranking(self.question3)

        # Configura el objeto mock para devolver la lista de preguntas
        questions = Question.objects.filter(
            pk__in=[self.question3.pk, self.question2.pk, self.question1.pk]
        )
        mock_question_objects_all.return_value = questions

        # Obtiene las preguntas ordenadas por ranking
        ranked_questions = [q for q in QuestionManager.get_ranked_questions(3)]

        # Verifica que las preguntas estén ordenadas por ranking de mayor a menor
        mock_question_objects_all.assert_called_once()
        self.assertEqual(
            ranked_questions, [self.question1, self.question2, self.question3]
        )

    def test_get_serialized_questions(self):
        # Calcula el ranking para cada pregunta
        QuestionManager.calculate_ranking(self.question1)
        QuestionManager.calculate_ranking(self.question2)
        QuestionManager.calculate_ranking(self.question3)

        # Obteniene las preguntas serializadas
        serialized_questions = QuestionManager.get_serialized_questions(
            [self.question1, self.question2, self.question3]
        )

        # Verifica que las preguntas estén serializadas correctamente
        expected_result = [
            {
                "pk": self.question1.id,
                "title": "Question 1",
                "author": self.user1,
                "ranking": self.question1.ranking,
            },
            {
                "pk": self.question2.id,
                "title": "Question 2",
                "author": self.user2,
                "ranking": self.question2.ranking,
            },
            {
                "pk": self.question3.id,
                "title": "Question 3",
                "author": self.user3,
                "ranking": self.question3.ranking,
            },
        ]

        self.assertEqual(serialized_questions, expected_result)


class QuestionListViewTest(TestCase):
    """
    Clase de pruebas para la vista de lista de preguntas (`QuestionListView`).

    Esta clase de pruebas configura instancias de usuarios, preguntas, respuestas
    y feedbacks de prueba para evaluar el comportamiento de la vista de lista de preguntas.

    Métodos de prueba específicos se encargan de verificar el funcionamiento de la vista
    tanto para usuarios autenticados como para usuarios no autenticados.

    Métodos de prueba:
    - `test_question_list_view_authenticated_user`: Verifica la vista para usuarios autenticados.
    - `test_question_list_view_unauthenticated_user`: Verifica la vista para usuarios no autenticados.
    """

    def setUp(self):
        # Crea un usuario de ejemplo
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Crea algunas preguntas de ejemplo
        self.question1 = Question.objects.create(
            title="Pregunta 1",
            description="Descripción de la pregunta 1",
            author=self.user,
        )
        self.question2 = Question.objects.create(
            title="Pregunta 2",
            description="Descripción de la pregunta 2",
            author=self.user,
        )
        self.question3 = Question.objects.create(
            title="Pregunta 3",
            description="Descripción de la pregunta 3",
            author=self.user,
        )

        # Crea respuestas y feedbacks de prueba
        self.feedback1 = QuestionFeedback.objects.create(
            question=self.question1, author=self.user, value="like"
        )
        self.feedback2 = QuestionFeedback.objects.create(
            question=self.question2, author=self.user, value="dislike"
        )
        self.feedback3 = QuestionFeedback.objects.create(
            question=self.question3, author=self.user, value="dislike"
        )

        self.answer1 = Answer.objects.create(
            question=self.question1, author=self.user, value=4
        )
        self.answer2 = Answer.objects.create(
            question=self.question2, author=self.user, value=1
        )
        self.answer3 = Answer.objects.create(
            question=self.question3, author=self.user, value=1
        )

    def tearDown(self):
        # Elimina las instancias
        self.user.delete()

        self.question1.delete()
        self.question2.delete()
        self.question3.delete()

        self.feedback1.delete()
        self.feedback2.delete()
        self.feedback3.delete()

        self.answer1.delete()
        self.answer2.delete()
        self.answer3.delete()

    def test_question_list_view_authenticated_user(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Hace una solicitud GET a la vista con autenticación
        response = self.client.get(reverse("survey:question-list"))

        # Verifica que la respuesta sea exitosa (código 200)
        self.assertEqual(response.status_code, 200)

        # Verifica que las preguntas se han pasado al contexto
        context = [q["pk"] for q in response.context["questions"]]
        questions = [self.question1.pk, self.question2.pk, self.question3.pk]
        self.assertQuerysetEqual(context, questions)

        # Verifica que las respuestas y el feedback están en el contexto para un usuario autenticado
        for question in response.context["questions"]:
            self.assertIn("answer", question)
            self.assertTrue("like" in question or "dislike" in question)

    def test_question_list_view_unauthenticated_user(self):
        # Hace una solicitud GET a la vista sin autenticación
        response = self.client.get(reverse("survey:question-list"))

        # Verifica que la respuesta sea exitosa (código 200)
        self.assertEqual(response.status_code, 200)

        # Verifica que las preguntas se han pasado al contexto
        context = [q["pk"] for q in response.context["questions"]]
        questions = [self.question1.pk, self.question2.pk, self.question3.pk]
        self.assertQuerysetEqual(context, questions)

        # Verifica que las respuestas y el feedback no están en el contexto para un usuario no autenticado
        for question in response.context["questions"]:
            self.assertNotIn("answer", question)
            self.assertFalse("like" in question or "dislike" in question)


class AnswerQuestionErrorTestCase(TestCase):
    """
    Clase de pruebas para gestionar errores en la vista de respuesta a preguntas (`AnswerQuestion`).

    Esta clase de pruebas configura instancias de usuario y pregunta de prueba para evaluar
    el manejo de errores en la vista de respuesta a preguntas.

    Métodos de prueba específicos se centran en casos como respuestas de usuarios no autenticados,
    datos incompletos, valores no numéricos y valores fuera del rango permitido.

    Métodos de prueba:
    - `test_answer_question_no_authentication`: Verifica la respuesta para usuarios no autenticados.
    - `test_answer_question_incomplete_data`: Verifica el manejo de datos incompletos.
    - `test_answer_question_non_digit_value`: Verifica el manejo de valores no numéricos.
    - `test_answer_question_invalid_value`: Verifica el manejo de valores fuera del rango permitido.
    """

    def setUp(self):
        # Crea un usuario de ejemplo
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Crea una pregunta de ejemplo
        self.question = Question.objects.create(
            title="Test Question",
            description="This is a test question",
            author=self.user,
        )

    def tearDown(self):
        # Elimina las instancias
        self.user.delete()
        self.question.delete()

    def test_answer_question_no_authentication(self):
        # Simula una solicitud POST válida
        data = {
            "question_pk": self.question.pk,
            "value": "3",
        }
        response = self.client.post(reverse("survey:question-answer"), data)

        # Verifica que la respuesta sea una redirección
        self.assertEqual(response.status_code, 302)

    def test_answer_question_incomplete_data(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Simula una solicitud POST con datos incompletos
        data = {
            "question_pk": self.question.pk,
        }
        response = self.client.post(reverse("survey:question-answer"), data)

        # Verifica que la respuesta sea un JsonResponse con un mensaje de error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"ok": False, "error": "Datos incompletos"},
        )

    def test_answer_question_non_digit_value(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Simula una solicitud POST con un valor no numérico
        data = {
            "question_pk": self.question.pk,
            "value": "abc",
        }
        response = self.client.post(reverse("survey:question-answer"), data)

        # Verifica que la respuesta sea un JsonResponse con un mensaje de error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"ok": False, "error": "El valor no es digito: abc"},
        )

    def test_answer_question_invalid_value(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Simular una solicitud POST con un valor fuera del rango permitido
        data = {
            "question_pk": self.question.pk,
            "value": "10",
        }
        response = self.client.post(reverse("survey:question-answer"), data)

        # Verifica que la respuesta sea un JsonResponse con un mensaje de error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"ok": False, "error": "Valor invalido: 10"},
        )


class LikeDislikeQuestionErrorTestCase(TestCase):
    """
    Clase de pruebas para gestionar errores en la vista de votación a preguntas (`like_dislike_question`).

    Esta clase de pruebas configura instancias de usuario y pregunta de prueba para evaluar
    el manejo de errores en la vista de votación a preguntas.

    Métodos de prueba específicos se centran en casos como votos de usuarios no autenticados,
    datos incompletos y valores de votación no válidos.

    Métodos de prueba:
    - `test_like_dislike_question_no_authentication`: Verifica la respuesta para usuarios no autenticados.
    - `test_like_dislike_question_incomplete_data`: Verifica el manejo de datos incompletos.
    - `test_like_dislike_question_invalid_value`: Verifica el manejo de valores de votación no válidos.
    """

    def setUp(self):
        # Crea un usuario de ejemplo
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Crea una pregunta de prueba
        self.question = Question.objects.create(
            title="Test Question",
            description="This is a test question",
            author=self.user,
        )

    def tearDown(self):
        # Elimina las instancias
        self.user.delete()
        self.question.delete()

    def test_like_dislike_question_no_authentication(self):
        # Simula una solicitud POST válida
        data = {
            "question_pk": self.question.pk,
            "value": "like",
        }
        response = self.client.post(reverse("survey:question-like"), data)

        # Verifica que la respuesta sea una redirección
        self.assertEqual(response.status_code, 302)

    def test_like_dislike_question_incomplete_data(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Simula una solicitud POST con datos incompletos
        data = {
            "question_pk": self.question.pk,
        }
        response = self.client.post(reverse("survey:question-like"), data)

        # Verifica que la respuesta sea un JsonResponse con un mensaje de error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"ok": False, "error": "Datos incompletos"},
        )

    def test_like_dislike_question_invalid_value(self):
        # Autentica al usuario
        login_successful = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login_successful)

        # Simula una solicitud POST con un valor no válido
        data = {
            "question_pk": self.question.pk,
            "value": "invalid_value",
        }
        response = self.client.post(reverse("survey:question-like"), data)

        # Verifica que la respuesta sea un JsonResponse con un mensaje de error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"ok": False, "error": "Valor invalido: invalid_value"},
        )
