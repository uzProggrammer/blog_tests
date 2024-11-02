from django.urls import path
from admin_api import views
from admin_api import users_api
from admin_api import groups_api
from admin_api import blog_tests
from admin_api import fedbacks
from admin_api import message_admin

urlpatterns = [
    path('login/', views.login_api),
    path('stats/1/', views.row_stats_api),
    path('logs/', views.admin_logs_api),
    path('tests/', views.all_tests_api),
    path('tests/<int:pk>/', views.get_test_api),
    path('tests/<int:id>/create/', views.create_test_api),
    path('tests/<int:id>/delete/', views.delete_test_api),
    path('tests/<int:id>/update/', views.update_test_api),
    path('tests/<int:id>/update-quiz/', views.update_quiz_api),
    path('tests/create/', views.create_quiz_api),
    path('tests/<int:pk>/results/', views.results_api),
    path('tests/<int:pk>/results/<int:pk1>/', views.result_api),
    path('tests/<int:pk>/upload-docx/', views.create_questions_with_docx),
    path('tests/<int:pk>/upload-pdf/', views.create_questions_with_pdf),
    path('tests/<int:pk>/results/delete/', views.delete_results_api),
    path('tests/<int:pk>/results/change/', views.change_results_api),


    path('users/', users_api.all_users_api),
    path('users/<str:username>/', users_api.get_user_api),
    path('users/<str:username>/update/', users_api.update_user_api),
    path('users/<str:username>/delete/', users_api.delete_user_api),
    path('users/<str:username>/update-password/', users_api.update_password_api),
    path('users/<str:username>/blog-tests-results/', users_api.get_user_dtm_results),

    path('groups/', groups_api.get_groups_api),
    path('groups/create/', groups_api.create_group_api),
    path('groups/<int:id>/blog-tests/', groups_api.get_dtms),
    path('groups/<int:group_id>/', groups_api.get_group_api),
    path('groups/<int:group_id>/add-user/', groups_api.add_student_to_group_api),
    path('groups/<int:group_id>/remove-user/', groups_api.remove_student_from_group_api),

    path('blog-tests/', blog_tests.get_quizes),
    path('blog-tests/<int:pk>/', blog_tests.get_blog_test),
    path('blog-tests/<int:pk>/edit/', blog_tests.edit_blog_test),
    path('blog-tests/delete-question/<int:pk>/', blog_tests.delete_question),
    path('blog-tests/<int:pk>/results/', blog_tests.get_results),
    path('blog-tests/<int:pk>/results/<int:pk1>/', blog_tests.get_result),
    path('blog-tests/<int:pk>/edit-question/<int:pk1>/', blog_tests.edit_question),
    path('blog-tests/<int:pk>/add-question/<int:pk1>/', blog_tests.add_question),
    path('blog-tests/<int:pk>/edit/<int:pk1>/', blog_tests.edit_quiz),
    path('blog-tests/<int:pk>/create-scince/', blog_tests.create_quiz),
    path('blog-tests/get-groups/', blog_tests.get_groups),
    path('blog-tests/create/', blog_tests.create_dtm),
    path('blog-tests/<int:pk>/results/change/', blog_tests.change_results_api),
    path('blog-tests/<int:pk>/results/delete/', blog_tests.delete_results_api),


    
    path('feedbacks/', fedbacks.all_fedbacks_api),
    path('feedbacks/<int:id>/', fedbacks.get_fedback_api),
    path('feedbacks/<int:id>/change/', fedbacks.set_is_true_api),

    
    path('messages/', message_admin.all_messages_api),
    path('messages/<int:pk>/', message_admin.get_chat_api),
    path('messages/<int:pk>/send-message/', message_admin.send_message_api),
]