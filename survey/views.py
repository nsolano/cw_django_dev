from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from survey.models import Question, Answer


class QuestionListView(ListView):
    model = Question


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


def answer_question(request):
    question_pk = request.POST.get('question_pk')
    value = request.POST.get('value')   
    if not question_pk or not value:
        return JsonResponse({'ok': False, 'error': 'Datos incompletos'})
    #question = Question.objects.filter(pk=question_pk)[0]
    try:
        question = Question.objects.filter(pk=question_pk)[0]
        author=request.user
    except Exception as ex:
        return JsonResponse({'ok': False, 'error': f'{ex}'})
    #answer = Answer.objects.get(question=question, author=request.user)
    #answer.value = request.POST.get('value')
    #answer.save()
    if not value.isdigit():
        return JsonResponse({'ok': False, 'error': 'Valor invalido'})
    
    print(value)
    return JsonResponse({'ok': True})

def like_dislike_question(request):
    question_pk = request.POST.get('question_pk')
    value = request.POST.get('value')
    
    if not question_pk or not value:
        return JsonResponse({'ok': False, 'error': 'Datos incompletos'})
    
    try:
        question = Question.objects.filter(pk=question_pk)[0]
    except Exception as ex:
        return JsonResponse({'ok': False, 'error': f'{ex}'})    

    if value == 'like':
        print(value)
    elif value == 'dislike':
        print(value)
    else:
        return JsonResponse({'ok': False, 'error': f'Valor no válido: {value}'})

    
    return JsonResponse({'ok': True})

