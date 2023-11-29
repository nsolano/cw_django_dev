from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from survey.models import Question, Answer, QuestionFeedback


class QuestionListView(ListView):
    model = Question
    template_name = 'survey/question_list.html'

    def calculate_ranking(self, question):
        # Cálculo del ranking
        answers = Answer.objects.filter(question=question).count()
        likes = QuestionFeedback.objects.filter(question=question,
                                                value='like').count()
        dislikes = QuestionFeedback.objects.filter(question=question,
                                                   value='dislike').count()

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

    def get_queryset(self):
        # Ordenamiento segun el ranking
        questions = Question.objects.all()

        for question in questions:
            question.ranking = self.calculate_ranking(question)
            question.save()

        questions = questions.order_by('-ranking').all()[:20]

        return questions

    def get_context_data(self, **kwargs):
        context = {'questions': []}
        user = self.request.user

        # Serialización de las preguntas
        serialized_questions = [{'pk': question.id,
                                 'title': question.title, 
                                 'author': question.author,
                                 'ranking': question.ranking
                                 } for question in self.object_list]

        # Agregación de las respuestas a cada pregunta
        if user.is_authenticated:
            for question in serialized_questions:
                answers = Answer.objects.filter(
                    question_id=question['pk'],
                    author=user).values('value')

                if answers.exists():
                    question['answer'] = answers[0].get('value')
                else:
                    question['answer'] = 0

                feedback = QuestionFeedback.objects.filter(
                    question_id=question['pk'],
                    author=user).values('value')

                if feedback.exists():
                    if feedback[0].get('value')  == 'like':
                        question['like'] = True
                    elif feedback[0].get('value')  == 'dislike':
                        question['dislike'] = True

        context['questions'] = serialized_questions


        return context


class QuestionCreateView(CreateView):
    model = Question
    fields = ['title', 'description']
    redirect_url = ''

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['title', 'description']
    template_name = 'survey/question_form.html'


@require_POST
@login_required
def answer_question(request):
    question_pk = request.POST.get('question_pk')
    value = request.POST.get('value')
    author=request.user

    if not question_pk or not value:
        return JsonResponse({'ok': False, 'error': 'Datos incompletos'})

    if not value.isdigit():
        return JsonResponse({'ok': False, 'error': 'Valor invalido'})

    try:
        question = Question.objects.filter(pk=question_pk)[0]
    except Exception as ex:
        return JsonResponse({'ok': False, 'error': f'{ex}'})

    try:
        answer = Answer.objects.get(question=question, author=author)
        answer.value = value
    except Answer.DoesNotExist:
        answer = Answer(
            question = question,
            author = author,
            value = value,
        )

    answer.save()

     # Llama a la vista QuestionListView para recalcular el ranking
    question_list = QuestionListView().get_queryset()
    question_ranking = [{'pk': question.id,                                 
                        'ranking': question.ranking
                        } for question in question_list]

    return JsonResponse({'ok': True, 'questions': question_ranking})


@require_POST
@login_required
def like_dislike_question(request):
    question_pk = request.POST.get('question_pk')
    value = request.POST.get('value')
    author=request.user

    if not question_pk or not value:
        return JsonResponse({'ok': False, 'error': 'Datos incompletos'})

    if value not in ('like', 'dislike'):
        return JsonResponse({'ok': False, 'error': f'Valor invalido: {value}'})

    try:
        question = Question.objects.filter(pk=question_pk)[0]
    except Exception as ex:
        return JsonResponse({'ok': False, 'error': f'{ex}'})

    try:
        feedback = QuestionFeedback.objects.get(question=question, author=author)
        feedback.value = value
    except QuestionFeedback.DoesNotExist:
        feedback = QuestionFeedback(
            question = question,
            author = author,
            value = value,
        )

    feedback.save()

    # Llama a la vista QuestionListView para recalcular el ranking
    question_list = QuestionListView().get_queryset()
    question_ranking = [{'pk': question.id,                                 
                        'ranking': question.ranking
                        } for question in question_list]

    return JsonResponse({'ok': True, 'questions': question_ranking})
