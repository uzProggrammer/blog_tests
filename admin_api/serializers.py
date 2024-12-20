from admin_api.models import AdminLog
from quizes.models import DTM, Answer, DtmResult, Feedback, Question, Quiz, Result, Variant
from users.models import ChatWithAdmin, Group, MessageForAdmin, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'jins','date_brith', 'image', 'ball', 'full_name']

class AdminLogUserSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.full_name')
    created_at = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = AdminLog
        fields = ['user', 'action', 'created_at', 'href','type']

class QuizSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'countinuis_time', 'is_public', 'scince']


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'text', 'is_correct']

class TestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    ball = serializers.FloatField()
    variants = VariantSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'created_at', 'ball', 'variants']


    def update(self, instance:Question, validated_data:dict):
        print(validated_data)
        instance.text = validated_data.get('text', instance.text)
        instance.ball = validated_data.get('ball', instance.ball)
        instance.variants.all().delete()
        for variant in validated_data['variants']:
            variant_obj = Variant.objects.create(text=variant['text'], is_correct=variant['is_correct'], quiz=instance.quiz, question=instance)
        instance.save() # instance = model
        return instance


class AnswerSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    user = UserSerializer()
    variant = VariantSerializer()

    class Meta:
        model = Answer
        fields = ['id', 'user', 'is_correct', 'created_at', 'variant']


class AnswerWithQuizSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    user = UserSerializer()
    variant = VariantSerializer()
    question = QuizSerializer()

    class Meta:
        model = Answer
        fields = ['id', 'user', 'is_correct', 'created_at', 'variant', 'question']


class ResultSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    user = UserSerializer()
    answers = AnswerSerializer(many=True)
    quiz = QuizSerializer()

    class Meta:
        model = Result
        fields = ['id', 'user', 'quiz', 'score', 'created_at', 'time_token', 'correct_answers', 'wrong_answers', 'answers', 'is_cheater']


class GroupSerializer(serializers.ModelSerializer):
    students = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'students', 'description']

class GroupSerializerWithOutStudents(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name', 'description']

class UserSerializerWithGroup(serializers.ModelSerializer):
    guruhlar = GroupSerializerWithOutStudents(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'jins','date_brith', 'image', 'ball', 'full_name', 'guruhlar']


class DTMSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format='%Y-%m-%d')
    end_date = serializers.DateTimeField(format='%Y-%m-%d')
    countinuis_time = serializers.TimeField(format='%H:%M:%S')
    group = GroupSerializerWithOutStudents()

    class Meta:
        model = DTM
        fields = ['id', 'title', 'start_date', 'end_date', 'countinuis_time', 'question_count', 'scinces', 'group']


class QuizWithTests(serializers.ModelSerializer):
    questions = TestSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions']

class DTMWithQuizsSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format='%Y-%m-%d')
    end_date = serializers.DateTimeField(format='%Y-%m-%d')
    countinuis_time = serializers.TimeField(format='%H:%M:%S')
    group = GroupSerializerWithOutStudents()
    quizs = QuizWithTests(many=True)
    groups = GroupSerializer(many=True)

    class Meta:
        model = DTM
        fields = ['id', 'title', 'start_date', 'end_date', 'countinuis_time', 'question_count', 'scinces', 'group', 'quizs', 'groups']

class DTMResultSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    user = UserSerializer()
    answers = AnswerWithQuizSerializer(many=True)
    quizs = QuizWithTests(many=True)
    dtm = DTMSerializer()

    class Meta:
        model = DtmResult
        fields = ['id','user','score','created_at','correct_answers', 'wrong_answers', 'time_token', 'place', 'answers', 'quizs', 'dtm', 'is_cheater']

class GroupForDTMSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(source='id')
    label = serializers.CharField(source='name')

    class Meta:
        model = Group
        fields = ['value', 'label']


class TestWithOutVariantsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    ball = serializers.FloatField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'created_at', 'ball',]

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    question = TestWithOutVariantsSerializer()
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    quiz = QuizSerializer()

    class Meta:
        model = Feedback
        fields = ('id', 'user', 'text', 'created_at', 'question', 'quiz', 'is_true')

class FeedbackWithVariantsSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    question = TestSerializer()
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    quiz = QuizSerializer()

    class Meta:
        model = Feedback
        fields = ('id', 'user', 'text', 'created_at', 'question', 'quiz', 'is_true', 'send_ball')

class MessageForAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    user1 = UserSerializer()

    class Meta:
        model = MessageForAdmin
        fields = ("user","message", "created_at", 'is_read', "is_admin_message", 'user1')

class ChatWithAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    messages = MessageForAdminSerializer(many=True)

    class Meta:
        model = ChatWithAdmin
        fields = ("id", "user", "created_at", "messages", 'last_message')