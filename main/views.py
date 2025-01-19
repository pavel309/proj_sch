import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
# from pygments import highlight
# from pygments.formatters import HtmlFormatter
# from pygments.lexers import PythonLexer

from .forms import RegisterForm, AddSnippetForm, LoginForm
from main.models import Snippet



# Функция для проверки, является ли пользователь администратором
def is_admin(user):
    return user.username == 'vasya'  # Замените 'admin' на имя вашего администратора

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

# Редактирование сниппета администратором
@login_required
@user_passes_test(is_admin)
def edit_snippet(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if request.method == 'POST':
        snippet.condition = request.POST.get('condition')
        snippet.count = request.POST.get('count')
        snippet.save()
        messages.add_message(request, messages.SUCCESS, "Сниппет успешно обновлён!")
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
    context = get_base_context(request, "Добавление нового сниппета")
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
            messages.add_message(request, messages.SUCCESS, "Сниппет успешно добавлен")
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
    context = get_base_context(request, "Просмотр сниппета")
    try:
        record = Snippet.objects.get(id=id)
        context["addform"] = AddSnippetForm(
            initial={
                "user": record.user.username if record.user != None else "AnonymousUser",
                "name": record.name,
                "condition" : record.condition,
                "count" : record.count,
                "send_user" : record.send_user,
                "text" : record.text,
            }
        )
        # 1. Поменяли название переменной в контексте
        # context["code_html_str"] = highlight(record.code, PythonLexer(), HtmlFormatter())
        # 2. Добавил файл стилей в static со стилем, который получил через HtmlFormatter().get_style_defs(".highlight")
    except Snippet.DoesNotExist:
        raise Http404
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
    context = get_base_context(request, "Мои сниппеты")
    context["data"] = Snippet.objects.filter(user=request.user)
    return render(request, "pages/view_snippets.html", context)
