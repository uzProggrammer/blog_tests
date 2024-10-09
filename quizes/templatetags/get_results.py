from django import template

from quizes.models import DTM, Answer, DtmResult, Question, Quiz, Result
from users.models import User

from django.db.models import Sum

register = template.Library()

@register.filter(name='get_results')
def get_results(test: Quiz, user:User):
    if user.is_anonymous:
        return []
    results = Result.objects.filter(quiz=test, user=user)
    return results

class eee:
    def __init__(self):
        self.users = []

    def add_user(self, user):
        self.users.append(user)

    def get_users(self):
        return self.users
    
    def clear_users(self):
        self.users = []

    def __str__(self):
        return str(self.users)

u = eee()

@register.filter(name='format_result')
def format_result(result: Result, last: bool = False):
    if result.user not in u.get_users():
        u.add_user(result.user)
        if last:
            u.clear_users()
        return True
    else:
        if last:
            u.clear_users()
        return False
    

@register.filter
def get_trues(result: DtmResult, question: Question):
    dtm = result.dtm
    answers = question.answers.all().filter(dtm=dtm, is_correct=True).count()
    return answers

@register.filter
def get_ball(result: DtmResult, question: Question):
    dtm = result.dtm
    answers = question.answers.filter(dtm=dtm, is_correct=True)
    answers_scope = answers.aggregate(score=Sum('quiz__ball'))
    return answers_scope['score'] or 0

@register.simple_tag
def get_total_ball(question: Question, user: User, dtm: DTM):
    result = DtmResult.objects.filter(user=user, dtm=dtm).first()
    if not result:
        return 'danger'
    answer = Answer.objects.filter(quiz=question, dtm=dtm, user=user).first()
    if not answer or not answer.is_correct:
        return 'danger'
    if answer.is_correct:
        return'success'
    
@register.simple_tag
def set_score(result: DtmResult, counter:int, page):
    counter = (page-1)*10+counter
    result.place = counter
    result.save()
    return result.place

@register.simple_tag
def get_chosen_variant(question: Question, user: User, dtm: DTM):
    answer = Answer.objects.filter(quiz=question, dtm=dtm, user=user).first()
    return f"{answer.chosen_variant}" if answer.is_correct else f"{answer.chosen_variant} ({answer.true_variant})"

@register.filter
def is_ended(dtm: DTM, user: User):
    result = DtmResult.objects.filter(user=user, dtm=dtm).first()
    if not result:
        return False
    return True