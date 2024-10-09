from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from.models import Answer, Question, Quiz, Result, StartTime, Variant

# Django Pagination
from django.core.paginator import Paginator
from django.db.models import Q


def quiz_list(request):
    search = request.GET.get('search', '')
    quizzes = Quiz.objects.filter(Q(title__icontains=search) | Q(description__icontains=search)|Q(scince__icontains=search), is_public=True).order_by('-id')
    paginator = Paginator(quizzes, 15)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.get_page(page_number)
    except:
        raise Http404("Page does not exist")
    return render(request, 'quizes/all.html', {'page_obj': page_obj,'search': search, 'is_page': request.GET.get('page', None)})

def get_questions_view(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/')
    quiz = get_object_or_404(Quiz, id=id)
    questions = quiz.questions.all().order_by('?')
    start_time,created = StartTime.objects.get_or_create(user=request.user, quiz=quiz, is_ended=False)
    return render(request, 'quizes/quiz.html', {'quiz': quiz, 'questions': questions, 'start_time': start_time})

def submit_view(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/')
    quiz = get_object_or_404(Quiz, id=id)
    start_time = StartTime.objects.get(user=request.user, quiz=quiz, is_ended=False)
    if request.method != 'POST':
        return Http404()
    ball = 0
    result = Result.objects.create(user=request.user, quiz=quiz, score=ball)
    for i,j in request.POST.items():
        if i=='csrfmiddlewaretoken':
            continue
        try:
            question = Question.objects.get(id=i,quiz=quiz)
            answer = Variant.objects.get(id=j, question=question,quiz=quiz)
        except:
            return HttpResponse('Invalid answer')
        answer1 = Answer.objects.create(user=request.user, quiz=question, variant=answer, is_correct=answer.is_correct)
        result.answers.add(answer1)
        if answer.is_correct:
            ball += question.ball
    result.score = ball
    result.time = (timezone.now() - start_time.date_created).total_seconds()
    result.save()
    start_time.is_ended = True
    start_time.save()
    request.user.ball += ball
    request.user.save()
    return JsonResponse({'result':result.id})

def result_view(request, id, id1):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/result/{id1}')
    quiz = get_object_or_404(Quiz, id=id)
    result = get_object_or_404(Result, user=request.user, quiz=quiz, id=id1)
    top_score = Result.objects.filter(quiz=quiz).order_by('-score', 'time').first()
    last_score = Result.objects.filter(quiz=quiz).order_by("score", '-time').first()
    return render(request, 'quizes/result.html', {'quiz': quiz,'result': result, 'top_score': top_score, 'last_score': last_score})

def result_view1(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/result/')
    quiz = get_object_or_404(Quiz, id=id)
    result = Result.objects.filter(user=request.user, quiz=quiz).order_by('-score', 'time').first()
    if not result:
        return HttpResponseRedirect(f'/tests/{id}/')
    top_score = Result.objects.filter(quiz=quiz).order_by('-score', 'time').first()
    last_score = Result.objects.filter(quiz=quiz).order_by("score", '-time').first()
    return render(request, 'quizes/result.html', {'quiz': quiz,'result': result, 'top_score': top_score, 'last_score': last_score})

def results_view(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/results/')
    quiz = get_object_or_404(Quiz, id=id)
    results = Result.objects.filter(quiz=quiz).order_by('-score', 'time')
    return render(request, 'quizes/results.html', {'quiz': quiz,'results': results})