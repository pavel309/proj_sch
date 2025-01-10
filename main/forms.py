from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
            }
        ),
    )
    password = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            }
        ),
    )


CHOICES = [("0", "Публичный сниппет"), ("1", "Приватный сниппет")]


class AddSnippetForm(forms.Form):
    name = forms.CharField(
        label="Название", max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    
    user = forms.CharField(
        label="Пользователь",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "disabled": "",
            }
        ),
        required=False,
    )

    condition = forms.CharField(
        label="Состояние", max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    count = forms.CharField(
        label="Количество", max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    send_user = forms.CharField(
        label="Имя поставщика", max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    code = forms.CharField(
        label="Описание",
        max_length=5000,
        widget=forms.Textarea(attrs={"class": "form-control", "style": "height:500px"}),
    )
