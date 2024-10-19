from django.urls import path

from. import views

urlpatterns = [
    path('', views.quiz_list, name='all_quizes'),
    path('<int:id>/', views.get_questions_view, name='get_quiz'),
    path('<int:id>/start/', views.start_quiz_view, name='start_quiz'),
    path('<int:id>/feedback/', views.feedback_view, name='feedback_quiz'),
    path('<int:id>/submit/', views.submit_view, name='submit_quiz'),
    path('<int:id>/result/<int:id1>/', views.result_view, name='quiz_result'),
    path('<int:id>/result/', views.result_view1, name='quiz_result1'),
    path('<int:id>/results/', views.results_view, name='quiz_result1'),
    path('<int:id>/results/download/', views.export_persons_to_excel, name='quiz_result1'),
]