from django.utils import timezone
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from requests import get
from quizes.models import DTM, Answer, DtmResult, Question, Result, StartTime, Variant
from django.db.models import Q

def get_all_blog_tests(request: HttpRequest):
    search = request.GET.get('q', '')
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login/')
    group = request.user.guruhlar.all()[0]
    blog_tests = DTM.objects.filter(Q(title__icontains=search),group=group)
    blog_tests1 = DTM.objects.filter(Q(title__icontains=search),group=None)
    blog_tests = blog_tests | blog_tests1

    paginator = Paginator(blog_tests, 10)
    page_number = request.GET.get('page', 1)
    if not str(page_number).isdigit():
        page_number = 1
    if int(page_number) > paginator.num_pages:
        page_number = paginator.num_pages
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog_tests/all.html', {'blog_tests': blog_tests, 'page_obj': page_obj, "object":paginator, 'search': search})

def get_blog_test(request: HttpRequest, pk: int):
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login/')
    group = request.user.guruhlar.all()[0]
    blog_test = DTM.objects.filter(pk=pk, group=group)
    blog_test1 = DTM.objects.filter(pk=pk, group=None)
    blog_test = blog_test or blog_test1
    if not blog_test.exists():
        return render(request, '404.html', {})
    return render(request, 'blog_tests/blog_test.html', {'blog_test': blog_test[0]})

def get_quizes(request: HttpRequest, pk:int):
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login/')
    group = request.user.guruhlar.all()[0]
    blog_test = DTM.objects.filter(pk=pk, group=group)
    blog_test1 = DTM.objects.filter(pk=pk, group=None)
    blog_test = blog_test or blog_test1
    if not blog_test.exists():
        return render(request, '404.html', {})
    result = DtmResult.objects.filter(dtm=blog_test[0], user=request.user).first()
    if result is not None:
        started_time = StartTime.objects.filter(dtm=blog_test[0], user=request.user)
        started_time = started_time.first()
        started_time.is_ended = True
        started_time.save()
        return render(request, '404.html', {}, status=404)
    started_time = StartTime.objects.filter(dtm=blog_test[0], user=request.user)
    if not started_time.exists():
        started_time = StartTime.objects.create(dtm=blog_test[0],user=request.user)
    else:
        started_time = started_time.first()
    return render(request, 'blog_tests/quizes.html', {'blog_test': blog_test[0], 'started_time': started_time})

def post_quiz(request: HttpRequest, pk:int):
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login/')
    group = request.user.guruhlar.all()[0]
    blog_test = DTM.objects.filter(pk=pk, group=group)
    blog_test1 = DTM.objects.filter(pk=pk, group=None)
    blog_test = blog_test or blog_test1
    if not blog_test.exists():
        return render(request, '404.html', {})
    started_time = StartTime.objects.filter(dtm=blog_test[0], user=request.user, is_ended=False).first()
    if started_time is None:
        return render(request, '404.html', {})
    result = DtmResult.objects.create(
        dtm=blog_test[0],
        user=request.user,
        score=0,
        time=(timezone.now()-started_time.date_created).total_seconds()
    )
    for i,j in request.POST.items():
        if i=='csrfmiddlewaretoken':
            continue
        question = Question.objects.filter(pk=int(i)).first()
        if question is None:
            continue
        result.quizs.add(question.quiz)
        variant = Variant.objects.filter(pk=int(j)).first()
        if variant is None:
            continue
        answer = Answer.objects.create(
            dtm=blog_test[0],
            user=request.user,
            quiz=question,
            variant=variant,
            is_correct=variant.is_correct,
            question=question.quiz,
        )
        result.answers.add(answer)
        if variant.is_correct:
            result.score += question.ball
        c=1
        for variant in question.variants.all():
            if variant.is_correct:
                c+=1
                answer.true_variant = "A" if c==1 else "B" if c==2 else "C" if c==3 else "D"
                c-=1
            if variant.id == int(j):
                answer.chosen_variant = "A" if c==1 else "B" if c==2 else "C" if c==3 else "D"
                c+=1
        answer.save()
    result.save()
    started_time.is_ended = True
    started_time.save()
    return JsonResponse({'result': result.id})

def get_result(request: HttpRequest, pk:int, pk1:int):
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login/')
    group = request.user.guruhlar.all()[0]
    blog_test = DTM.objects.filter(pk=pk, group=group)
    blog_test1 = DTM.objects.filter(pk=pk, group=None)
    blog_test = blog_test or blog_test1
    if not blog_test.exists():
        return render(request, '404.html', {})
    result = DtmResult.objects.filter(pk=pk1, dtm=blog_test[0], user=request.user).first()
    if result is None:
        return render(request, '404.html', {})
    return render(request, 'blog_tests/result.html', {'blog_test':blog_test[0], 'result': result})

def result_list(request: HttpRequest, pk:int):
    dtm = get_object_or_404(DTM, pk=pk)
    results = DtmResult.objects.filter(dtm=dtm).order_by('-score','-time')

    paginator = Paginator(results, 10)
    page_number = request.GET.get('page', 1)
    if not str(page_number).isdigit():
        page_number = 1
    if int(page_number) > paginator.num_pages:
        page_number = paginator.num_pages
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog_tests/result_list.html', {'results': results, 'page_obj': page_obj, 'object':paginator, 'blog_test':dtm})