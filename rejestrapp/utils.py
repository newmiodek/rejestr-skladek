import hashlib
import typing
from django import forms
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .errors import BadGroszeException
from .forms import NewEasyTransactionFormBase, NewTransactionFormBase
from .models import Debt, Register, SignupToken


def gr_to_zl(gr: int) -> str:
    if not isinstance(gr, int):
        raise BadGroszeException("Amount of grosze should be an integer")
    str_gr = str(gr)
    if gr > 0:
        if gr >= 100:
            return str_gr[:-2] + "." + str_gr[-2:]
        elif gr >= 10:
            return "0." + str_gr
        else:  # 1 <= gr <= 9
            return "0.0" + str_gr
    elif gr < 0:
        if gr <= -100:
            return str_gr[:-2] + "." + str_gr[-2:]
        elif gr <= -10:
            return "-0." + str_gr[1:]
        else:  # -1 >= gr >= -9
            return "-0.0" + str_gr[1:]
    else:  # gr == 0
        return "0.00"


def dont_be_logged_in(cls):
    cls._dont_be_logged_in__original_dispatch = cls.dispatch

    def new_dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            response = HttpResponseRedirect(reverse("rejestrapp:userspace"))
            response.content = b"dont_be_logged_in"
            return response
        return cls._dont_be_logged_in__original_dispatch(self, request, *args, **kwargs)

    cls.dispatch = new_dispatch
    return cls


def render_error_page(
    request: HttpRequest, message: str, status_code: int, back: str
) -> HttpResponse:
    return render(
        request,
        "rejestrapp/error.html",
        {"error_message": message, "back": back},
        status=status_code,
    )


def generate_new_transaction_form_class(new_transaction_users: QuerySet[User]) -> type:
    fields = {
        f"value_for_{new_transaction_user.pk}": forms.FloatField(
            label=f"Wartość dla {new_transaction_user.username}",
            step_size=0.01,
            required=True,
        )
        for new_transaction_user in new_transaction_users
    }

    return type("NewTransactionForm", (NewTransactionFormBase,), fields)


def generate_new_easy_transaction_form_class(
    new_transaction_users: QuerySet[User],
) -> type:
    fields = {
        f"value_for_{new_transaction_user.pk}": forms.FloatField(
            label=f"Ile dołożył {new_transaction_user.username}",
            min_value=0.0,
            step_size=0.01,
            required=True,
        )
        for new_transaction_user in new_transaction_users
    }

    return type("NewEasyTransactionForm", (NewEasyTransactionFormBase,), fields)


def check_if_can_be_viewed(cls):
    cls._check_if_can_be_viewed__original_dispatch = cls.dispatch

    def new_dispatch(self, request, *args, **kwargs):
        register = get_object_or_404(Register, pk=kwargs["register_id"])
        if register.users.filter(pk=request.user.pk).count() != 1:
            return render_error_page(
                request,
                "Nie jesteś członkiem tego rejestru",
                403,
                reverse("rejestrapp:userspace"),
            )

        if not register.all_accepted:
            return render_error_page(
                request,
                "Ten rejestr jeszcze nie został zaakceptowany "
                "przez wszystkich zaproszonych",
                403,
                reverse("rejestrapp:userspace"),
            )

        kwargs.update({"check_if_can_be_viewed__register": register})

        return cls._check_if_can_be_viewed__original_dispatch(
            self, request, *args, **kwargs
        )

    cls.dispatch = new_dispatch
    return cls


def check_for_errors_in_invite_view(request, register_id):
    register = get_object_or_404(Register, pk=register_id)
    try:
        this_debt = register.debt_set.get(user=request.user.pk)
    except Debt.DoesNotExist:
        return (
            None,
            None,
            render_error_page(
                request,
                "Nie zaproszono Cie do tego rejestru",
                403,
                reverse("rejestrapp:userspace"),
            ),
        )
    if this_debt.accepted:
        return (
            None,
            None,
            render_error_page(
                request,
                "Już zaakceptowałeś/aś to zaproszenie",
                403,
                reverse("rejestrapp:userspace"),
            ),
        )
    return register, this_debt, None


VALID_TOKEN_CHARS = (
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
)


def account_activation_link_validation(func):
    def get(self, request: HttpRequest, *args, **kwargs):
        url_token = kwargs["token"]
        token_well_formed = len(url_token) == 64
        if token_well_formed:
            for i in range(64):
                if url_token[i] not in VALID_TOKEN_CHARS:
                    token_well_formed = False
                    break
        if token_well_formed:
            hashed_form_token = hashlib.sha256(bytes(url_token, "utf-8")).hexdigest()
            token_query = SignupToken.objects.filter(pk=hashed_form_token)
            if token_query.count() == 0:
                return render_error_page(
                    request,
                    "Nieprawidłowy link aktywacyjny",
                    403,
                    reverse("rejestrapp:signup"),
                )
            token = typing.cast(SignupToken, token_query.first())
            user = User.objects.get(email=token.email)
            token_query.delete()
            kwargs.update({"account_activation_link_validation__user": user})
            return func(self, request, *args, **kwargs)
        else:
            return render_error_page(
                request,
                "Nieprawidłowy link aktywacyjny",
                403,
                reverse("rejestrapp:signup"),
            )

    return get
