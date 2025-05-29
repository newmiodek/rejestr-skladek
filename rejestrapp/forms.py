from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput, TextInput

from .models import SignupToken


class MustNameNewTransactionWidget(TextInput):
    """
    Widget for displaying an extra validation message
    about the name of a new transaction.
    """

    template_name = "rejestrapp/must_name_new_transaction_widget.html"


class NewTransactionFormBase(forms.Form):
    """
    This class is used as a base for dynamically creating
    manual transaction form classes. Code that derives form classes
    from it should add fields for values for users.
    """

    transaction_name = forms.CharField(
        label="Nazwa transakcji", max_length=128, widget=MustNameNewTransactionWidget
    )


class ValidatedExpenseWidget(NumberInput):
    """
    Widget for displaying and extra validation message
    about the supplied value of the expense.
    """

    template_name = "rejestrapp/validated_expense_widget.html"


class NewEasyTransactionFormBase(forms.Form):
    """
    This class is used as a base for dynamically creating
    simplified transaction form classes. Code that derives form classes
    from it should add fields for values for users.
    """

    transaction_name = forms.CharField(
        label="Nazwa transakcji",
        max_length=128,
        widget=MustNameNewTransactionWidget,
        required=True,
    )
    expense = forms.FloatField(
        label="Ile wydano",
        min_value=0.0,
        step_size=0.01,
        widget=ValidatedExpenseWidget,
        required=True,
    )


class TransactionVoteForm(forms.Form):
    """
    Form for voting on a transaction.
    """

    supports = forms.BooleanField(
        label="Zgadzasz sie na tą transakcje?", required=False
    )
    wants_remove = forms.BooleanField(
        label="Chcesz anulować tą transakcje?", required=False
    )


class RequiredFormSet(forms.BaseFormSet):
    """
    A formset with added functionality that prohibits
    empty values on fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
            form.use_required_attribute = True


class UserToNewRegisterForm(forms.Form):
    """
    A form to be used by the formset for adding users to a register.
    """

    username = forms.CharField(label="Nazwa użytkownika", max_length=150)


class NewRegisterNameForm(forms.Form):
    """
    A form that will be used by the formset for adding new users to a register.
    It holds the new register's name.
    """

    name = forms.CharField(label="Nazwa rejestru", max_length=128)


class TokenedUserCreationForm(UserCreationForm):
    """
    A form for signing up that requires a token to register.
    """

    signup_token = forms.CharField(
        label="Token Rejestracyjny",
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "off"}),
        help_text="Wklej token rejestracyjny",
    )

    def validate_token(self):
        form_token = self.cleaned_data.get("signup_token")
        token = SignupToken.objects.filter(pk=form_token).first()
        if token is None or token.used_up:
            error = ValidationError("Niepoprawny token", code="invalid_token")
            self.add_error("signup_token", error)

    def clean(self):
        self.validate_token()
        return super().clean()


class UserCreationFormWithEmail(UserCreationForm):
    email = forms.EmailField(
        label="E-mail",
        help_text=" ",
        required=True,
        widget=forms.EmailInput(),
        max_length=254,
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def validate_email_unique(self):
        form_email = self.cleaned_data.get("email").lower()
        email_query = User.objects.filter(email=form_email)

        if email_query.count() != 0:
            token_query = SignupToken.objects.filter(email=form_email)
            if token_query.count() == 0:
                error = ValidationError(
                    "Istnieje już konto z takim e-mailem", code="used_email"
                )
                self.add_error("email", error)
