from django.shortcuts import render, redirect,get_object_or_404
from .forms import *
from .models import *
from django.contrib import messages
from django.views import generic
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from youtubesearchpython import VideosSearch
import requests
import wikipedia as wiki

# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')

def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            note = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            note.save()
            messages.success(request, "Notes added successfully")
            return redirect('notes') 
    else:
        form = NotesForm()
    
    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailedView(generic.DetailView):
    model=Notes

def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            work = Homework(user=request.user,
                            subject=request.POST['subject'],
                            title=request.POST['title'], 
                            description=request.POST['description'],
                            due=request.POST['due'],
                            is_finished=request.POST.get('is_finished') == 'on' )
            work.save()
            messages.success(request, "Homework added successfully")
            return redirect('homework') 
    else:
        form=HomeworkForm
    
    homework=Homework.objects.filter(user=request.user)
    homework_done = False
    if len(homework) == 0:
        homework_done = True
    context={'homeworks':homework,'homeworks_done':homework_done,'form':form}
    return render(request,'dashboard/homework.html',context)

def mark_as_completed(request, homework_id):
    try:
        homework = Homework.objects.get(id=homework_id, user=request.user)
        homework.is_finished = not homework.is_finished
        homework.save()
        messages.success(request, "Homework status updated successfully")
    except Homework.DoesNotExist:
        messages.error(request, "Homework item does not exist")
    return redirect('homework')

def delete_work(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

def youtube(request):
    if request.method=="POST":
        form=DashBoardForm(request.POST)
        text=request.POST['text']
        video=VideosSearch(text,limit=20)
        result_list=[]
        for i in video.result()['result']:
            result_dict={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnails':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'viewcount':i['viewCount']['short'],
                'published':i['publishedTime'],
            }
            desc=''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc+=j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form=DashBoardForm()
    context={'form':form}
    return render(request,'dashboard/youtube.html',context)


def todo(request):
    if request.method == "POST":
        form = ToDoForm(request.POST)
        if form.is_valid():
            # Save the form with the user and is_finished handled by the form itself
            form.instance.user = request.user
            form.save()
            messages.success(request, "Todo added successfully")
            return redirect('todo')  # Redirect to the same page after adding a todo
    else:
        form = ToDoForm()

    todos = Todo.objects.filter(user=request.user)
    todos_done = len(todos) == 0
    context = {'todos': todos, 'form': form, 'todos_done': todos_done}
    return render(request, 'dashboard/todo.html', context)

def delete_todo(request, pk=None):
    todo = get_object_or_404(Todo, id=pk)
    todo.delete()
    return redirect('todo')  # Redirect to the todo view after deletion

def update_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.is_finished = not todo.is_finished
    todo.save()
    
    messages.success(request, "Todo status updated successfully.")
    
    return redirect('todo')
def books(request):
    if request.method == "POST":
        form = DashBoardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        
        for i in range(10):
            volume_info = answer['items'][i]['volumeInfo']
            image_links = volume_info.get('imageLinks', {})
            result_dict = {
                'title': volume_info.get('title'),
                'subtitle': volume_info.get('subtitle'),
                'description': volume_info.get('description'),
                'count': volume_info.get('pageCount'),
                'categories': volume_info.get('categories'),
                'rating': volume_info.get('averageRating'),  # Changed 'pageRating' to 'averageRating'
                'thumbnail':image_links.get('thumbnail'),
                'preview': volume_info.get('previewLink'),
            }
            result_list.append(result_dict)
        
        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashBoardForm()
        context = {'form': form}
        return render(request, 'dashboard/books.html', context)

def dictionary(request):
    if request.method == "POST":
        form = DashBoardForm(request.POST)
        text = request.POST.get('text')
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/" + text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0].get('example', 'No example available')
            synonyms = answer[0]['meanings'][0]['definitions'][0].get('synonyms', [])
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms
            }
        except (IndexError, KeyError):
            context = {
                'form': form,
                'input': 'Word not found or API error'
            }
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashBoardForm()
        context = {'form': form}
        return render(request, 'dashboard/dictionary.html', context)

def wikipedia(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashBoardForm(request.POST)
        
        try:
            search = wiki.page(text)
            context = {
                'form': form,
                'title': search.title,
                'link': search.url,
                'details': search.summary
            }
        except wikipedia.exceptions.DisambiguationError as e:
            context = {
                'form': form,
                'title': "Disambiguation Error",
                'link': "#",
                'details': f"Disambiguation error occurred. Options: {e.options}"
            }
        except wikipedia.exceptions.PageError:
            context = {
                'form': form,
                'title': "Page not found",
                'link': "#",
                'details': "The requested page could not be found on Wikipedia."
            }
        return render(request, 'dashboard/wikipedia.html', context)
    else:
        form = DashBoardForm()
        context = {'form': form}
        return render(request, 'dashboard/wikipedia.html', context)
def conversion(request):
    if request.method == "POST":
        form=ConversionForm(request.POST)
        if request.POST['measurement']=='length':
            measurementForm=ConversionLength()
            context={
                'form':form,
                'm_form':measurementForm,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first=='yard' and second=='foot':
                        answer=f'{input} yard={int(input)*3} foot'
                    if first=='foot' and second=='yard':
                        answer=f'{input} foot={int(input)/3} yard'
                context={
                'form':form,
                'm_form':measurementForm,
                'input':True,
                'answer':answer
            }
        if request.POST['measurement']=='mass':
            measurementForm=ConversionMass()
            context={
                'form':form,
                'm_form':measurementForm,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first=='pound' and second=='kilogram':
                        answer=f'{input} pound ={int(input)*0.453592} kilogram'
                    if first=='kilogram' and second=='pound':
                        answer=f'{input} kilogram={int(input)*2.20462} pound'
                context={
                'form':form,
                'm_form':measurementForm,
                'input':True,
                'answer':answer
            }
        return render(request,'dashboard/conversion.html',context)
    else:
        form=ConversionForm()
        context={'form':form,
             'input':False
             }
        return render(request,'dashboard/conversion.html',context)
    
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully")
            return redirect("login")
    else:
        form = UserRegistrationForm()
        
    context = {'form': form}
    return render(request, 'dashboard/register.html', context)

def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todo_done=True
    else:
        todo_done=False
    context={'homeworks':homeworks,
             'todos':todos,
             'homework_done':homework_done,
             'todo_done':todo_done}
    return render(request,'dashboard/profile.html',context)

def logout_view(request):
    return render(request, 'dashboard/logout1.html')
    