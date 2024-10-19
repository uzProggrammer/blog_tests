from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse

from users.models import User
from.models import Answer, Feedback, Question, Quiz, Result, StartTime, Variant
import pandas as pd


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

def start_quiz_view(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/')
    quiz = get_object_or_404(Quiz, id=id)
    start_time = StartTime.objects.create(user=request.user, quiz=quiz, is_ended=False)
    return HttpResponseRedirect(f'/tests/{id}/')

def get_questions_view(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/')
    quiz = get_object_or_404(Quiz, id=id)
    questions = quiz.questions.all().order_by('?')
    try:
        start_time = StartTime.objects.get(user=request.user, quiz=quiz, is_ended=False)
    except:
        return HttpResponseRedirect(f'/tests/')
    return render(request, 'quizes/quiz.html', {'quiz': quiz, 'questions': questions, 'start_time': start_time})

def submit_view(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/')
    quiz = get_object_or_404(Quiz, id=id)
    ball = 0
    try:
        start_time = StartTime.objects.get(user=request.user, quiz=quiz, is_ended=False)
    except:
        return HttpResponseRedirect('/tests/')
    result = Result.objects.create(user=request.user, quiz=quiz, score=ball)
    result.time = (timezone.now() - start_time.date_created).total_seconds()
    result.save()
    if request.method != 'POST':
        return Http404()
    for question in quiz.questions.all():
        try:
            v = request.POST[str(question.id)]
            answer = Variant.objects.get(id=v, question=question,quiz=quiz)
            answer1 = Answer.objects.create(user=request.user, quiz=question, variant=answer, is_correct=answer.is_correct)
            feedback = Feedback.objects.filter(user=request.user, question=question, quiz=quiz)
            if feedback.exists():
                feedback = feedback.last()
                feedback.answer = answer1
                feedback.save()
            result.answers.add(answer1)
            if answer.is_correct:
                ball += question.ball
            
            c=1;c1=1
            for k in question.variants.all():
                if k.is_correct:
                    answer1.true_variant = "A" if c==1 else "B" if c==2 else "C" if c==3 else "D"
                if k.id==answer.id:
                    answer1.chosen_variant = "A" if c1==1 else "B" if c1==2 else "C" if c1==3 else "D"
                answer1.save()
                c+=1
                c1+=1
                answer1.save()
            result.answers.add(answer1)
        except:
            c=1
            true_variant=''
            for k in question.variants.all():
                if k.is_correct:
                    true_variant = "A" if c==1 else "B" if c==2 else "C" if c==3 else "D"
                c+=1
            answer = Answer.objects.create(user=request.user, quiz=question, variant=None, true_variant=true_variant, chosen_variant="Tanlanmagan")
            result.answers.add(answer)

    # for i,j in request.POST.items():
    #     if i=='csrfmiddlewaretoken':
    #         continue
    #     try:
    #         question = Question.objects.get(id=i,quiz=quiz)
    #         answer = Variant.objects.get(id=j, question=question,quiz=quiz)
    #     except:
    #         return HttpResponse('Invalid answer')
    #     answer1 = Answer.objects.create(user=request.user, quiz=question, variant=answer, is_correct=answer.is_correct)
    #     feedback = Feedback.objects.filter(user=request.user, question=question, quiz=quiz)
    #     if feedback.exists():
    #         feedback = feedback.first()
    #         feedback.answer = answer1
    #         feedback.save()
    #     result.answers.add(answer1)
    #     if answer.is_correct:
    #         ball += question.ball
        
    #     c=1;c1=1
    #     for k in question.variants.all():
    #         if k.is_correct:
    #             answer1.true_variant = "A" if c==1 else "B" if c==2 else "C" if c==3 else "D"
    #         if k.id==int(j):
    #             answer1.chosen_variant = "A" if c1==1 else "B" if c1==2 else "C" if c1==3 else "D"
    #         answer1.save()
    #         c+=1
    #         c1+=1
    result.score = ball
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
    result = get_object_or_404(Result, quiz=quiz, id=id1)
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


def export_persons_to_excel(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    persons = quiz.results.all().order_by('-score', 'time').values()

    df = pd.DataFrame(list(persons))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={quiz.title} - testining natijalari.xlsx'
    df['created_at'] = df['created_at'].apply(lambda x: str(x.strftime('%Y-%m-%d %H:%M:%S')))
    df['user_id'] = User.objects.filter(id__in=df['user_id']).values_list('full_name', flat=True)
    del df['quiz_id']
    df['time'] = df['time'].apply(lambda x: f"{(x//3600):02d}:{(x%3600//60):02d}:{(x%60):02d}")
    df.rename(columns={'id': 'O\'rin', 'user_id': 'Foydalanuvchi', 'created_at': "Yuborilgan sana", "time": 'Sarflangan vaqt', 'ball': 'To\'plagan ball'}, inplace=True)
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response

def feedback_view(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(f'/login/?next=/tests/{id}/feedback/')
    quiz = get_object_or_404(Quiz, id=id)
    if request.method == 'POST':
        debug = request.POST.get('debug')
        question = str(request.POST.get('question_id'))
        if not question or not question.isdigit():
            return JsonResponse({'status':'error', "msg":'savol topilmadi'})
        question = get_object_or_404(Question, id=int(question), quiz=quiz)
        if debug:
            feedback = Feedback.objects.create(user=request.user, quiz=quiz, text=debug, question=question)
            return JsonResponse({'status':"ok", 'msg':"Xabar adminga yuborildi"})
        return HttpResponseRedirect(f'/tests/{id}/')
    return HttpResponseRedirect(f'/tests/')