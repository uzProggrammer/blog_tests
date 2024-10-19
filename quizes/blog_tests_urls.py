from django.urls import path
from . import blog_tests as views

urlpatterns = [
    path('', views.get_all_blog_tests,),
    path('<int:pk>/', views.get_blog_test,),
    path('<int:pk>/quizes/', views.get_quizes,),
    path('<int:pk>/submit/', views.post_quiz,),
    path('<int:pk>/result/<int:pk1>/', views.get_result,),
    path('<int:pk>/results/', views.result_list,),
    path('<int:pk>/results-as-excel/', views.export_results_to_excel,),
]
