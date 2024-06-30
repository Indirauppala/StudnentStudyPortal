from django.urls import path
from . import views
from .views import logout_view
urlpatterns=[
    path('',views.home,name='home'),
    path('home',views.home,name='home'),
    path('notes',views.notes,name='notes'),
    path('delete_note/<int:pk>',views.delete_note,name='delete-note'),
    path('notes_detail/<int:pk>',views.NotesDetailedView.as_view(),name='notes_detail'),
    path('homework',views.homework,name='homework'),
    path('homework/mark_as_completed/<int:homework_id>/', views.mark_as_completed, name='mark_as_completed'),
    path('delete_work/<int:pk>',views.delete_work,name='delete-work'),
    path('youtube',views.youtube,name='youtube'),
    path('todo',views.todo,name='todo'),
    path('delete_todo/<int:pk>',views.delete_todo,name='delete_todo'),
    path('update_todo/<int:todo_id>/', views.update_todo, name='update-todo'),
    path('books',views.books,name='book'),
    path('dictionary',views.dictionary,name='dicionary'),
    path('wikipedia',views.wikipedia,name='wikipedia'),
    path('conversion',views.conversion,name='conversion'),
    path('profile',views.profile,name='profile'),
    path('logout/', logout_view, name='logout_view'),
]