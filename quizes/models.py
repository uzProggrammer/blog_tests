from django.db import models
from users.models import Group, User
from django.utils import timezone


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    countinuis_time = models.TimeField()

    is_public = models.BooleanField(default=False)

    scince = models.TextField(max_length=200)
    docx_file = models.FileField(upload_to='quizes/docx_files', null=True, blank=True)

    def get_questions_random(self):
        return self.questions.all().order_by('?')

    def get_scinces(self):
        return self.scince.split()
    def __str__(self):
        return self.title
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ball = models.FloatField(default=0)


    def get_random_variants(self):
        return self.variants.all().order_by('?')

    def __str__(self):
        return self.text

class Variant(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='variants')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='variants')

    def __str__(self):
        return self.text




class Answer(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='answers')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    quiz = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False)

    question = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    dtm = models.ForeignKey('DTM', on_delete=models.CASCADE, related_name='answers', null=True, blank=True)

    chosen_variant = models.CharField(max_length=200, null=True, blank=True)
    true_variant = models.CharField(max_length=200, null=True, blank=True)
    
    with_feedback = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='results')
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    answers = models.ManyToManyField(Answer, related_name='results')
    time = models.IntegerField(null=True, blank=True)

    is_cheater = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def correct_answers(self):
        return self.answers.filter(variant__is_correct=True).count()
    
    def wrong_answers(self):
        return self.answers.filter(variant__is_correct=False).count()
    
    def time_token(self):
        return f"{(self.time//3600):02d}:{(self.time%3600//60):02d}:{(self.time%60):02d}"
    
    def get_answers_as_list(self):
        return [i.chosen_variant for i in self.answers.all()]
    
    def similar_variants(self, test, similar_value=75):
        data = test.results.exclude(id=self.id)
        data1 = []
        for result in data:
            similars = 0
            for i,answer in enumerate(self.answers.all()):
                for j,answer1 in enumerate(result.answers.all()):
                    if i==j:
                        if answer.chosen_variant==answer1.chosen_variant:
                            similars+=1
            similars_percent = (similars/self.answers.count())*100
            if similars_percent<similar_value:
                data = data.exclude(id=result.id)
            else:
                data1.append(similars_percent)
        return data, data1

    
class DTM(models.Model):
    quizs = models.ManyToManyField(Quiz, related_name='dtms')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='dtms', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    countinuis_time = models.TimeField()

    def status(self):
        return 'Boshlanmagan' if self.start_date > timezone.now() else 'Boshlangan' if self.start_date < timezone.now() < self.end_date else 'Tugangan'
    
    def question_count(self):
        return self.quizs.aggregate(models.Count('questions'))['questions__count']

    def scinces(self):
        return ','.join(self.quizs.all().values_list('scince', flat=True))

    def groups(self):
        return Group.objects.all()


class DtmResult(models.Model):
    quizs = models.ManyToManyField(Quiz, related_name='DTM_results')
    dtm = models.ForeignKey(DTM, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='DTM_results')
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    answers = models.ManyToManyField(Answer, related_name='DTM_results')
    time = models.IntegerField(null=True, blank=True)
    
    place = models.IntegerField(null=True, blank=True)

    is_cheater = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def correct_answers(self):
        return self.answers.filter(variant__is_correct=True).count()
    
    def wrong_answers(self):
        return self.answers.filter(variant__is_correct=False).count()
    
    def time_token(self):
        return f"{(self.time//3600):02d}:{(self.time%3600//60):02d}:{(self.time%60):02d}"
    
    def similar_variants(self, test, similar_value=75):
        data = test.results.all()
        data1 = []
        for result in data:
            similars = 0
            for i,answer in enumerate(self.answers.all()):
                for j,answer1 in enumerate(result.answers.all()):
                    if i==j:
                        if answer.chosen_variant==answer1.chosen_variant:
                            similars+=1
            similars_percent = (similars/self.answers.count())*100
            if similars_percent<similar_value:
                data = data.exclude(id=result.id)
            else:
                data1.append(similars_percent)
        return data, data1


class StartTime(models.Model):
    dtm = models.ForeignKey(DTM, on_delete=models.CASCADE, related_name='start_times', null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='start_times', null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='start_times')
    is_ended = models.BooleanField(default=False)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    blog_test = models.ForeignKey(DTM, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    is_true = models.BooleanField(default=False)

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    send_ball = models.BooleanField(default=False)