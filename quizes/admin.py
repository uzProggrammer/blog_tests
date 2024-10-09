from django.contrib import admin
from.models import Quiz, Question, Answer, Variant, StartTime, Result, DTM, DtmResult

# Register your models here.
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Variant)
admin.site.register(StartTime)
admin.site.register(Result)
admin.site.register(DTM)
admin.site.register(DtmResult)