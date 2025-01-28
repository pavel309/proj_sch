import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
# from pygments import highlight
# from pygments.formatters import HtmlFormatter
# from pygments.lexers import PythonLexer

from .forms import RegisterForm, AddSnippetForm, LoginForm
from .models import Snippet
from .models import RepairRequest
from .forms import RepairRequestForm



# Функция для проверки, является ли пользователь администратором
def is_admin(user):
    return user.is_superuser == 1  

# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Регистрация прошла успешно!")
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_snippet(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    
    if request.method == 'POST':
        snippet.delete()
        messages.add_message(request, messages.SUCCESS, "Данные успешно удалёны!")
        return redirect('my_snippets')
    
    return render(request, 'confirm_delete.html', {'snippet': snippet})

# Редактирование инвентаря администратором
@login_required
@user_passes_test(is_admin)
def edit_snippet(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if request.method == 'POST':
        snippet.condition = request.POST.get('condition')
        snippet.count = request.POST.get('count')
        snippet.status = request.POST.get('status')
        snippet.text = request.POST.get('text')

        # Сохраняем изменения
        snippet.save()
        messages.add_message(request, messages.SUCCESS, "Данные успешно обновлёны!")
        return redirect('view_snippet', id=id)
    return render(request, 'edit_snippet.html', {'snippet': snippet})




def get_base_context(request, pagename):
    return {
        "pagename": pagename,
        "loginform": LoginForm(),
        "user": request.user,
    }


def index_page(request):
    context = get_base_context(request, "Инвентарь")

    if request.method == "GET":
        snippet_id: str | None = request.GET.get("snippet_id", "")
        if snippet_id != "":
            return redirect("view_snippet", id=snippet_id)

    return render(request, "pages/index.html", context)


def add_snippet_page(request):
    context = get_base_context(request, "Добавление нового инвентаря")
    if request.method == "POST":
        addform = AddSnippetForm(request.POST)
        if addform.is_valid():
            record = Snippet(
                name=addform.data["name"],
                text=addform.data["text"],
                condition = addform.data["condition"],
                count = addform.data["count"],
                send_user = addform.data["send_user"],
                creation_date=datetime.datetime.now(),
                user=request.user if request.user.is_authenticated else None,
            )
            record.save()
            id = record.id
            messages.add_message(request, messages.SUCCESS, "Инвентарь успешно добавлен")
            return redirect("view_snippet", id=id)
        else:
            messages.add_message(request, messages.ERROR, "Некорректные данные в форме")
            return redirect("add_snippet")
    else:
        context["addform"] = AddSnippetForm(
            initial={
                "user": request.user.username if request.user.is_authenticated else "AnonymousUser",
            }
        )
    return render(request, "pages/add_snippet.html", context)


def view_snippet_page(request, id):
    context = get_base_context(request, "Просмотр инвентаря")
    try:
        record = Snippet.objects.get(id=id)
        context["record"] = record
        context["addform"] = AddSnippetForm(
            initial={
                "user": record.user.username if record.user != None else "AnonymousUser",
                "name": record.name,
                "condition" : record.condition,
                "count" : record.count,
                "send_user" : record.send_user,
                "text" : record.text,
                "status" : record.status,
            }
        )
    except Snippet.DoesNotExist:
        messages.error(request, "Инвентарь с указанным ID не найден.")
        return redirect('index')
    return render(request, "pages/view_snippet.html", context)


def login_page(request):
    if request.method == "POST":
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.data["username"]
            password = loginform.data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, "Авторизация успешна")
            else:
                messages.add_message(request, messages.ERROR, "Неправильный логин или пароль")
        else:
            messages.add_message(request, messages.ERROR, "Некорректные данные в форме авторизации")
    return redirect("index")


def logout_page(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Вы успешно вышли из аккаунта")
    return redirect("index")


@login_required
def my_snippets_page(request):
    context = get_base_context(request, "Мой инвентарь")
    if request.user.is_superuser:
        context["data"] = Snippet.objects.all()
    else:
        context["data"] = Snippet.objects.filter(user=request.user)
    return render(request, "pages/view_snippets.html", context)


@login_required
def create_repair_request(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if request.method == 'POST':
        form = RepairRequestForm(request.POST)
        if form.is_valid():
            repair_request = RepairRequest(
                snippet=snippet,
                user=request.user,
                description=form.cleaned_data['description'],
            )
            repair_request.save()
            messages.add_message(request, messages.SUCCESS, "Заявка на ремонт успешно создана!")
            return redirect('view_snippet', id=id)
    else:
        form = RepairRequestForm()
    
    context = get_base_context(request, "Создание заявки на ремонт")
    context['form'] = form
    context['snippet'] = snippet
    return render(request, 'pages/create_repair_request.html', context)



@login_required
def repair_requests_list(request):
    if request.user.is_superuser:
        repair_requests = RepairRequest.objects.all()
    else:
        repair_requests = RepairRequest.objects.filter(user=request.user)
    
    context = get_base_context(request, "Список заявок на ремонт")
    context['repair_requests'] = repair_requests
    return render(request, 'pages/repair_requests_list.html', context)


# Редактирование заявки администратором
@login_required
@user_passes_test(is_admin)
def edit_repair_request(request, id):
    repair = get_object_or_404(RepairRequest, id=id)
    if request.method == 'POST':
        repair.status = request.POST.get('status')
        # Сохраняем изменения
        repair.save()
        messages.add_message(request, messages.SUCCESS, "Данные успешно обновлёны!")
        return redirect('repair_requests_list')
    return render(request, 'pages/edit_repair_request.html', {'repair': repair})