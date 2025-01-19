import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
# from pygments import highlight
# from pygments.formatters import HtmlFormatter
# from pygments.lexers import PythonLexer

from main.forms import AddSnippetForm, LoginForm
from main.models import Snippet


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
                code=addform.data["code"],
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
