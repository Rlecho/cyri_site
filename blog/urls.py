from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.home, name='home'),
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<int:article_id>/download/', views.download_file, name='download_file'),
    path('article/<int:article_id>/comment/', views.add_comment, name='add_comment'),
    # Contact public
    path('contact/', views.contact, name='contact'),

    # Authentification

    # Gestion des messages (admin)
    path('dashboard/contact/', views.contact_messages, name='contact_messages'),
    path('dashboard/contact/<int:message_id>/', views.contact_message_detail, name='contact_message_detail'),
    path('dashboard/contact/<int:message_id>/delete/', views.delete_contact_message, name='delete_contact_message'),

    # Administration
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/article/create/', views.admin_article_create, name='admin_article_create'),
    path('dashboard/article/<int:article_id>/edit/', views.admin_article_edit, name='admin_article_edit'),
    path('dashboard/article/<int:article_id>/delete/', views.admin_article_delete, name='admin_article_delete'),
    path('dashboard/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('dashboard/comment/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
]



 
    
   
    
    
    
    
    
