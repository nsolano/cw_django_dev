"""
Módulo de vistas y funciones asociadas para la aplicación.

Este módulo contiene las definiciones de vistas basadas en funciones y clases para
la gestión de preguntas, respuestas y retroalimentación de usuarios.

Vistas Funcionales:
    - answer_question(request): Permite a los usuarios votar o responder preguntas.
    - like_dislike_question(request): Maneja la retroalimentación positiva o negativa a preguntas.

Vistas Basadas en Clases:
    - QuestionListView(ListView): Muestra una lista de preguntas ordenadas por ranking.
    - QuestionCreateView(CreateView): Permite a los usuarios crear nuevas preguntas.
    - UserQuestionListView(LoginRequiredMixin, ListView): Muestra las preguntas creadas 
      por el usuario autenticado.
    - QuestionUpdateView(UpdateView): Permite a los usuarios actualizar preguntas existentes.
    - QuestionDeleteView(DeleteView): Permite a los usuarios eliminar sus propias preguntas.

Funciones Auxiliares:
    - calculate_ranking(question): Calcula el ranking de una pregunta basándose en respuestas 
      y retroalimentación.
    - get_ranked_questions(n): Obtiene las preguntas mejor clasificadas.
    - get_serialized_questions(questions): Serializa las preguntas para su presentación.

"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from survey.models import Answer, Question, QuestionFeedback


class QuestionListView(ListView):
    """
    Vista basada en clase para mostrar una lista de preguntas clasificadas por ranking.

    Esta vista utiliza la clase QuestionManager para obtener y mostrar preguntas ordenadas
    por ranking. También agrega información sobre las respuestas y feedback de un usuario
    autenticado.

    Atributos:
        - model (Question): El modelo de datos utilizado por la vista (Question).
        - template_name (str): La plantilla HTML utilizada para renderizar la vista.

    Métodos:
        - `get_context_data(**kwargs)`: Obtiene el contexto para renderizar la plantilla,
          incluyendo preguntas, respuestas y feedback.

    Parámetros:
        - **kwargs: Argumentos adicionales.

    Retorno:
        - dict: Un diccionario que contiene el contexto necesario para renderizar la
          plantilla HTML, incluyendo preguntas, respuestas y feedback.
    """

    model = Question
    template_name = "survey/question_list.html"

    def get_context_data(self, **kwargs):
        # Personaliza el contexto qeu se envía al front-end
        context = {"questions": []}
        user = self.request.user

        question_manager = QuestionManager()
        questions = question_manager.get_ranked_questions(20)
        serialized_questions = question_manager.get_serialized_questions(questions)

        # Agrega las respuestas a cada pregunta
        # Si el usuario está autenticado se muestra el contenido usado
        # en los botones de rating y like/dislike
        if user.is_authenticated:
            for question in serialized_questions:
                answers = Answer.objects.filter(
                    question_id=question["pk"], author=user
                ).values("value")

                if answers.exists():
                    question["answer"] = answers[0].get("value")
                else:
                    question["answer"] = 0

                feedback = QuestionFeedback.objects.filter(
                    question_id=question["pk"], author=user
                ).values("value")

                if feedback.exists():
                    if feedback[0].get("value") == "like":
                        question["like"] = True
                    elif feedback[0].get("value") == "dislike":
                        question["dislike"] = True

        context["questions"] = serialized_questions

        return context


class QuestionCreateView(CreateView):
    """
    Vista basada en clase para crear una nueva pregunta.

    Esta vista utiliza el formulario asociado al modelo Question para recoger datos del
    usuario y crear una nueva pregunta. El autor de la pregunta se establece como el
    usuario autenticado.

    Atributos:
        - model (Question): El modelo de datos utilizado por la vista (Question).
        - fields (List): Los campos del modelo que se incluirán en el formulario.
        - template_name (str): La plantilla HTML utilizada para renderizar la vista.

    Métodos:
        - `form_valid(form)`: Asigna el autor de la pregunta al usuario autenticado.
        - `get_success_url()`: Devuelve la URL a la que se redirige después de una creación
          exitosa.

    Parámetros:
        - form (ModelForm): El formulario que recoge los datos de la pregunta.

    Retorno:
        - HttpResponseRedirect: Una redirección a la URL especificada en get_success_url.
    """

    model = Question
    fields = ["title", "description"]
    template_name = "survey/question_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("survey:question-edit-list")


class UserQuestionListView(LoginRequiredMixin, ListView):
    """
    Vista basada en clase para mostrar una lista de preguntas creadas por el usuario autenticado.

    Esta vista utiliza la clase LoginRequiredMixin para asegurarse de que solo los usuarios
    autenticados pueden acceder a ella. Muestra una lista de preguntas filtradas por el
    usuario autenticado.

    Atributos:
        - model (Question): El modelo de datos utilizado por la vista (Question).
        - template_name (str): La plantilla HTML utilizada para renderizar la vista.
        - context_object_name (str): El nombre del objeto de contexto utilizado en la plantilla.

    Métodos:
        - `get_queryset()`: Devuelve el conjunto de preguntas filtrado por el usuario autenticado.

    Retorno:
        - QuerySet: El conjunto de preguntas filtrado."""

    model = Question
    template_name = "survey/question_list.html"
    context_object_name = "questions"

    def get_queryset(self):
        # Filtrar preguntas por el usuario autenticado
        return Question.objects.filter(author=self.request.user)


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista basada en clase para eliminar una pregunta.

    Esta vista utiliza la clase LoginRequiredMixin para asegurarse de que solo los usuarios
    autenticados pueden acceder a ella. Permite al usuario eliminar sus propias preguntas.

    Atributos:
        - model (Question): El modelo de datos utilizado por la vista (Question).
        - template_name (str): La plantilla HTML utilizada para renderizar la vista.

    Métodos:
        - `get_success_url()`: Devuelve la URL a la que se redirige después de una eliminación
          exitosa.
        - `get_queryset()`: Devuelve el conjunto de preguntas filtrado por el usuario autenticado.

    Retorno:
        - HttpResponseRedirect: Una redirección a la URL especificada en get_success_url.
    """

    model = Question
    template_name = "survey/question_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("survey:question-edit-list")

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtra las preguntas solo para el usuario autenticado
        return queryset.filter(author=self.request.user)


class QuestionUpdateView(UpdateView):
    """
    Vista basada en clase para actualizar una pregunta existente.

    Esta vista utiliza el formulario asociado al modelo Question para recoger datos del
    usuario y actualizar una pregunta existente.

    Atributos:
        - model (Question): El modelo de datos utilizado por la vista (Question).
        - fields (List): Los campos del modelo que se incluirán en el formulario.
        - template_name (str): La plantilla HTML utilizada para renderizar la vista.

    Métodos:
        - `get_success_url()`: Devuelve la URL a la que se redirige después de una actualización
          exitosa.

    Retorno:
        - HttpResponseRedirect: Una redirección a la URL especificada en get_success_url.
    """

    model = Question
    fields = ["title", "description"]
    template_name = "survey/question_form.html"

    def get_success_url(self):
        return reverse_lazy("survey:question-edit-list")


class QuestionManager:
    """
    Clase para gestionar preguntas y su ranking.

    Esta clase proporciona métodos estáticos para calcular el ranking de una pregunta,
    obtener una lista de preguntas clasificadas por ranking y serializar preguntas.

    Métodos:
        - `calculate_ranking(question)`: Calcula el ranking de una pregunta según el número
          de respuestas, likes, dislikes y la fecha de creación.
        - `get_ranked_questions(n)`: Obtiene una lista de las n preguntas mejor clasificadas
          por ranking.
        - `get_serialized_questions(questions)`: Serializa una lista de preguntas.

    Parámetros:
        - question (Question): Instancia de la clase Question para la cual se calculará
          el ranking.
        - n (int): Número de preguntas que se desea obtener en la lista clasificada.

    Retorno:
        Los métodos pueden devolver diferentes tipos de datos, como int, QuerySet o list,
        según la funcionalidad específica de cada uno.
    """

    @staticmethod
    def calculate_ranking(question):
        # Cálculo del ranking
        answers = Answer.objects.filter(question=question, value__range=(1, 5)).count()
        likes = QuestionFeedback.objects.filter(question=question, value="like").count()
        dislikes = QuestionFeedback.objects.filter(
            question=question, value="dislike"
        ).count()

        # Cada respuesta suma 10 puntos al ranking
        ranking = answers * 10
        # Cada like suma 5 puntos al ranking
        ranking += likes * 5
        # Cada dislike resta 3 puntos al ranking
        ranking -= dislikes * 3

        # Agrega 10 puntos si es del día de hoy
        if question.created == timezone.now().date():
            ranking += 10

        return ranking

    @staticmethod
    def get_ranked_questions(n):
        # Ordenamiento segun el ranking
        questions = Question.objects.all()

        for question in questions:
            question.ranking = QuestionManager.calculate_ranking(question)
            question.save()

        questions = questions.order_by("-ranking").all()[:n]

        return questions

    @staticmethod
    def get_serialized_questions(questions):
        # Serialización de las preguntas
        serialized_questions = [
            {
                "pk": question.id,
                "title": question.title,
                "author": question.author,
                "ranking": question.ranking,
            }
            for question in questions
        ]

        return serialized_questions


@require_POST
@login_required
def answer_question(request):
    """
    Vista para manejar respuestas a preguntas.

    Esta vista permite a los usuarios autenticados proporcionar respuestas numéricas
    a preguntas especificadas. La respuesta debe ser un dígito en el rango de 0 a 5.

    Parámetros:
        request (HttpRequest): La solicitud HTTP recibida.

    Retorno:
        HttpResponse: Una redirección a la página principal ("/") después de procesar
        la respuesta. En caso de datos incompletos, valores no numéricos o valores
        fuera del rango permitido, devuelve un JsonResponse con un mensaje de error.
    """

    # Extrae la información del request tipo POST
    question_pk = request.POST.get("question_pk")
    value = request.POST.get("value")
    author = request.user

    # Verifica la validez de la información extraída
    if not question_pk or not value:
        return JsonResponse({"ok": False, "error": "Datos incompletos"})

    if not value.isdigit():
        return JsonResponse({"ok": False, "error": f"El valor no es digito: {value}"})

    if int(value) not in range(6):
        return JsonResponse({"ok": False, "error": f"Valor invalido: {value}"})

    try:
        question = Question.objects.filter(pk=question_pk)[0]
    except Exception as ex:
        return JsonResponse({"ok": False, "error": f"{ex}"})

    if question.author == author:
        return JsonResponse(
            {"ok": False, "error": "No se puede votar tu propia pregunta"}
        )

    # Verifica si existe la entrada en el modelo Answer
    # de lo contrario lo crea usando los datos del request
    try:
        answer = Answer.objects.get(question=question, author=author)
        answer.value = value
    except Answer.DoesNotExist:
        answer = Answer(
            question=question,
            author=author,
            value=value,
        )

    # Guarda en la base de datos las entradas
    answer.save()

    # Redirige a /
    return redirect("/")


@require_POST
@login_required
def like_dislike_question(request):
    """
    Vista de manejo de votos (like/dislike) para preguntas.

    Esta vista permite a los usuarios autenticados votar por preguntas, expresando
    su preferencia ya sea con un "like", "dislike" u otro valor especificado.

    Parámetros:
        request (HttpRequest): La solicitud HTTP recibida.

    Retorno:
        HttpResponse: Una redirección a la página principal ("/") después de procesar
        el voto. En caso de datos incompletos o valores inválidos, devuelve un
        JsonResponse con un mensaje de error.
    """

    # Extrae la información del request tipo POST
    question_pk = request.POST.get("question_pk")
    value = request.POST.get("value")
    author = request.user

    # Verifica la validez de la información extraída
    if not question_pk or not value:
        return JsonResponse({"ok": False, "error": "Datos incompletos"})

    if value not in ("like", "dislike", "other"):
        return JsonResponse({"ok": False, "error": f"Valor invalido: {value}"})

    try:
        question = Question.objects.filter(pk=question_pk)[0]
    except Exception as ex:
        return JsonResponse({"ok": False, "error": f"{ex}"})

    if question.author == author:
        return JsonResponse(
            {"ok": False, "error": "No puedes votar tu propia pregunta"}
        )

    # Verifica si existe la entrada en el modelo QuestionFeedback
    # de lo contrario lo crea usando los datos del request
    try:
        feedback = QuestionFeedback.objects.get(question=question, author=author)
        feedback.value = value
    except QuestionFeedback.DoesNotExist:
        feedback = QuestionFeedback(
            question=question,
            author=author,
            value=value,
        )

    # Guarda en la base de datos las entradas
    feedback.save()

    # Redirige a /
    return redirect("/")
