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
    model = Question
    template_name = "survey/question_list.html"

    def get_context_data(self, **kwargs):
        context = {"questions": []}
        user = self.request.user

        question_manager = QuestionManager()
        questions = question_manager.get_ranked_questions(20)
        serialized_questions = question_manager.get_serialized_questions(questions)

        # Agregación de las respuestas a cada pregunta
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
    model = Question
    fields = ["title", "description"]
    template_name = "survey/question_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("survey:question-edit-list")


class UserQuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = "survey/question_list.html"
    context_object_name = "questions"

    def get_queryset(self):
        # Filtrar preguntas por el usuario autenticado
        return Question.objects.filter(author=self.request.user)


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question
    template_name = "survey/question_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("survey:question-edit-list")

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtra las preguntas solo para el usuario autenticado
        return queryset.filter(author=self.request.user)


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ["title", "description"]
    template_name = "survey/question_form.html"

    def get_success_url(self):
        return reverse_lazy("survey:question-edit-list")


class QuestionManager:
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

        # Agregar 10 puntos si es del día de hoy
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
    question_pk = request.POST.get("question_pk")
    value = request.POST.get("value")
    author = request.user

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
            {"ok": False, "error": "No puedes votar tu propia pregunta"}
        )

    try:
        answer = Answer.objects.get(question=question, author=author)
        answer.value = value
    except Answer.DoesNotExist:
        answer = Answer(
            question=question,
            author=author,
            value=value,
        )

    answer.save()

    return redirect("/")


@require_POST
@login_required
def like_dislike_question(request):
    question_pk = request.POST.get("question_pk")
    value = request.POST.get("value")
    author = request.user

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

    try:
        feedback = QuestionFeedback.objects.get(question=question, author=author)
        feedback.value = value
    except QuestionFeedback.DoesNotExist:
        feedback = QuestionFeedback(
            question=question,
            author=author,
            value=value,
        )

    feedback.save()

    return redirect("/")
