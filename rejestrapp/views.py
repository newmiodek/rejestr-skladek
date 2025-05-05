import random
import typing
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import F
from django.forms import formset_factory
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, View
from django.shortcuts import get_object_or_404, redirect, render
from .forms import (
    NewRegisterNameForm,
    RequiredFormSet,
    TokenedUserCreationForm,
    TransactionVoteForm,
    UserToNewRegisterForm,
)
from .models import (
    Debt,
    GroupTransaction,
    IndividualsTransaction,
    Register,
    SignupToken,
)
from .utils import (
    check_for_errors_in_invite_view,
    check_if_can_be_viewed,
    dont_be_logged_in,
    generate_new_easy_transaction_form_class,
    generate_new_transaction_form_class,
    gr_to_zl,
    render_error_page,
)


class UserspaceView(View):
    """
    This is a user's 'main menu'. Here they have a list of their registers
    as well as their invitations.
    """

    http_method_names = ["get", "options"]

    def get(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("rejestrapp:login"))
        accepted_registers = []
        accepted_invites = []
        not_accepted_invites = []
        for register in Register.objects.filter(users=request.user).order_by("name"):
            if register.all_accepted:
                accepted_registers.append(register)
            else:
                debt_set = register.debt_set
                if debt_set.get(user=request.user.pk).accepted:
                    accepted_invites.append(
                        (
                            register,
                            debt_set.filter(accepted=True).count(),
                            debt_set.count(),
                        )
                    )
                else:
                    not_accepted_invites.append(register)
        return render(
            request,
            "rejestrapp/userspace.html",
            {
                "accepted_registers": accepted_registers,
                "accepted_invites": accepted_invites,
                "not_accepted_invites": not_accepted_invites,
            },
        )


@dont_be_logged_in
class NoRepeatLoginView(LoginView):
    """
    The standart LoginView with an additional decorator
    that prevents logged-in users from accessing it.
    """

    pass


@dont_be_logged_in
class SignUpView(CreateView):
    """
    View for creating new users. When someone creates an account,
    they are automatically logged in. The decorator prevents
    logged-in users from accessing it.
    """

    form_class = TokenedUserCreationForm
    success_url = reverse_lazy("rejestrapp:userspace")
    template_name = "rejestrapp/signup.html"

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            token = SignupToken.objects.get(pk=form.cleaned_data["signup_token"])
            token.used_up = True
            token.save()
            self.object = form.save()
            new_user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, new_user)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)


@check_if_can_be_viewed
class RegisterView(LoginRequiredMixin, View):
    """
    View for displaying a register's data in a table.
    """

    http_method_names = ["get", "options"]

    def get(self, request: HttpRequest, *args, **kwargs):
        register = kwargs["check_if_can_be_viewed__register"]
        debts_for_display = []
        for debt in register.debt_set.all().order_by("user__username"):
            debts_for_display.append(
                {"name": debt.user.username, "balance": gr_to_zl(debt.balance)}
            )
        return render(
            request,
            "rejestrapp/register.html",
            {
                "debts": debts_for_display,
                "register": register,
                "transactions": GroupTransaction.objects.filter(
                    debts__register__pk=register.pk
                )
                .distinct()
                .order_by("is_settled", "init_date"),
                "back": reverse("rejestrapp:userspace"),
            },
        )


@check_if_can_be_viewed
class NewTransactionView(LoginRequiredMixin, View):
    """
    View for initiating and processing manual transactions.
    When accessed by GET, it displays a form with a field
    for every user in a register where values should be supplied.
    When POSTed to, it checks whether the values add up to zero
    and creates a new GroupTransaction object if they do.
    """

    http_method_names = ["get", "post", "options"]

    def get(self, request: HttpRequest, *args, **kwargs):
        register = kwargs["check_if_can_be_viewed__register"]
        form_class = generate_new_transaction_form_class(
            register.users.all().order_by("username")
        )
        form = form_class()

        return render(
            request,
            "rejestrapp/new_transaction.html",
            {
                "register": register,
                "form": form,
                "back": reverse(
                    "rejestrapp:register", kwargs={"register_id": register.pk}
                ),
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        register = kwargs["check_if_can_be_viewed__register"]
        form_class = generate_new_transaction_form_class(
            register.users.all().order_by("username")
        )
        form = form_class(request.POST)

        if form.is_valid():
            amount_sum = 0
            for k, v in form.cleaned_data.items():
                if k == "transaction_name":
                    continue
                amount_sum += round(v * 100)
            if amount_sum != 0:
                return render_error_page(
                    request,
                    "Wpisane wartości mają dodawać sie do zera",
                    422,
                    reverse(
                        "rejestrapp:new_transaction",
                        kwargs={"register_id": register.pk},
                    ),
                )
            group_transaction = GroupTransaction.objects.create(
                name=form.cleaned_data["transaction_name"], init_date=timezone.now()
            )
            for debt in Debt.objects.filter(register=register):
                group_transaction.debts.add(
                    debt,
                    through_defaults={
                        "amount": round(
                            form.cleaned_data[f"value_for_{debt.user.pk}"] * 100
                        )
                    },
                )
            return redirect(
                reverse(
                    "rejestrapp:transaction_vote",
                    kwargs={
                        "register_id": kwargs["register_id"],
                        "group_transaction_id": group_transaction.pk,
                    },
                )
            )
        else:
            return render_error_page(
                request,
                "Coś się nie zgadzało w Twoim zapytaniu",
                400,
                reverse(
                    "rejestrapp:new_transaction",
                    kwargs={"register_id": register.pk},
                ),
            )


@check_if_can_be_viewed
class NewEasyTransactionView(LoginRequiredMixin, View):
    """
    View for initiating and processing simplified transactions.
    When accessed by GET, it displays a form with a field
    for every user in a register where values should be supplied.
    When POSTed to, it checks whether the values add up to the supplied
    'expense' value, and creates a new GroupTransaction object if they do.
    The value of the expense gets split evenly among users and subtracted
    from their total, and then they amount of money each of them
    contributed gets added to their total.
    """

    http_method_names = ["get", "post", "options"]

    def get(self, request: HttpRequest, *args, **kwargs):
        register = kwargs["check_if_can_be_viewed__register"]
        form_class = generate_new_easy_transaction_form_class(
            register.users.all().order_by("username")
        )
        form = form_class()

        return render(
            request,
            "rejestrapp/new_easy_transaction.html",
            {
                "register": register,
                "form": form,
                "back": reverse(
                    "rejestrapp:register", kwargs={"register_id": register.pk}
                ),
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        register = kwargs["check_if_can_be_viewed__register"]
        form_class = generate_new_easy_transaction_form_class(
            register.users.all().order_by("username")
        )
        form = form_class(request.POST)

        if form.is_valid():
            sum = 0
            expense = round(form.cleaned_data["expense"] * 100)
            if expense < 0:
                return render_error_page(
                    request,
                    "Wydatek został źle podany",
                    422,
                    reverse(
                        "rejestrapp:new_easy_transaction",
                        kwargs={"register_id": register.pk},
                    ),
                )
            # a list with tuples (user_id, their_contribution)
            users_with_contributions = []
            for k, v in form.cleaned_data.items():
                if k.startswith("value_for_"):
                    value = round(v * 100)
                    users_with_contributions.append((int(k[10:]), value))
                    sum += value
            if sum != expense:
                return render_error_page(
                    request,
                    "Suma podanych dołożeń nie równa się wydatkowi",
                    422,
                    reverse(
                        "rejestrapp:new_easy_transaction",
                        kwargs={"register_id": register.pk},
                    ),
                )
            # convert to values with which to update users' balances
            users_with_changes = []
            divided_expense = expense // len(users_with_contributions)
            for u, c in users_with_contributions:
                users_with_changes.append([u, divided_expense - c])
            # randomly add the grosze that were left out after the division
            leftover = expense - divided_expense * len(users_with_contributions)
            who_to_charge = random.sample(users_with_changes, leftover)
            for charged in who_to_charge:
                charged[1] += 1

            group_transaction = GroupTransaction.objects.create(
                name=form.cleaned_data["transaction_name"], init_date=timezone.now()
            )
            for debt in Debt.objects.filter(register=register):
                group_transaction.debts.add(
                    debt,
                    through_defaults={
                        # set the amount for the user of this debt
                        # to the value that corresponds to them
                        # in the users_with_changes list
                        "amount": next(
                            uc for uc in users_with_changes if uc[0] == debt.user.pk
                        )[1]
                    },
                )
            return redirect(
                reverse(
                    "rejestrapp:transaction_vote",
                    kwargs={
                        "register_id": kwargs["register_id"],
                        "group_transaction_id": group_transaction.pk,
                    },
                )
            )


@check_if_can_be_viewed
class TransactionVoteView(LoginRequiredMixin, View):
    """
    Here members of a register get to decide whether to accept
    a proposed transaction. They can vote to accept or to remove
    a transaction. They have the option to vote for both
    accepting and removing at the same time.
    """

    http_method_names = ["get", "post", "options"]

    def get(self, request: HttpRequest, *args, **kwargs):
        group_transaction = get_object_or_404(
            GroupTransaction, pk=kwargs["group_transaction_id"]
        )
        vote_table_rows = []
        supports = False
        wants_remove = False
        for indiv in group_transaction.individualstransaction_set.all().order_by(
            "debt__user__username"
        ):
            if indiv.debt.user == request.user:
                supports = indiv.supports
                wants_remove = indiv.wants_remove

            if indiv.balance_before is not None:
                balance_before = gr_to_zl(indiv.balance_before)
                balance_after = gr_to_zl(indiv.balance_before + indiv.amount)
            else:
                balance_before = gr_to_zl(indiv.debt.balance)
                balance_after = gr_to_zl(indiv.debt.balance + indiv.amount)
            vote_table_rows.append(
                {
                    "indiv": indiv,
                    "balance_before": balance_before,
                    "balance_after": balance_after,
                    "amount": gr_to_zl(indiv.amount),
                }
            )
        form = TransactionVoteForm({"supports": supports, "wants_remove": wants_remove})
        return render(
            request,
            "rejestrapp/transaction_vote.html",
            {
                "register_name": kwargs["check_if_can_be_viewed__register"].name,
                "transaction_name": group_transaction.name,
                "vote_table_rows": vote_table_rows,
                "voting_allowed": not group_transaction.is_settled,
                "form": form,
                "register_id": kwargs["register_id"],
                "group_transaction_id": kwargs["group_transaction_id"],
                "back": reverse(
                    "rejestrapp:register",
                    kwargs={"register_id": kwargs["register_id"]},
                ),
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        group_transaction = get_object_or_404(
            GroupTransaction, pk=kwargs["group_transaction_id"]
        )
        if group_transaction.is_settled:
            return render_error_page(
                request,
                "Ta transakcja została już zatwierdzona, nie można zmienić zgód",
                403,
                reverse(
                    "rejestrapp:new_transaction",
                    kwargs={"register_id": kwargs["register_id"]},
                ),
            )
        form = TransactionVoteForm(request.POST)
        if form.is_valid():
            this_indiv = get_object_or_404(
                IndividualsTransaction,
                group_transaction=group_transaction,
                debt__user=request.user,
            )
            this_indiv.supports = form.cleaned_data["supports"]
            this_indiv.wants_remove = form.cleaned_data["wants_remove"]
            this_indiv.save()
            all_want_remove = True
            all_support = True
            all_indivs = IndividualsTransaction.objects.filter(
                group_transaction=group_transaction
            )
            for indiv in all_indivs:
                if not indiv.supports:
                    all_support = False
                if not indiv.wants_remove:
                    all_want_remove = False

            if all_want_remove:
                all_indivs.delete()
                group_transaction.delete()
                return redirect(
                    reverse(
                        "rejestrapp:register",
                        kwargs={"register_id": kwargs["register_id"]},
                    )
                )
            elif all_support:
                group_transaction.is_settled = True
                group_transaction.settle_date = timezone.now()
                group_transaction.save()
                for indiv in all_indivs:
                    debt = Debt.objects.get(pk=indiv.debt.pk)
                    indiv.balance_before = debt.balance
                    indiv.save()
                    debt.balance = F("balance") + indiv.amount
                    debt.save()
            return redirect(
                reverse(
                    "rejestrapp:transaction_vote",
                    kwargs={
                        "register_id": kwargs["register_id"],
                        "group_transaction_id": kwargs["group_transaction_id"],
                    },
                )
            )


class NewRegisterView(LoginRequiredMixin, View):
    """
    View for creating new registers. It operates on a form
    that accepts a variable number fields, each of which expects
    a username of an existing user.
    """

    http_method_names = ["get", "post", "options"]
    _usernames_prefix = "usernames"
    _register_name_prefix = "register_name"

    def get(self, request: HttpRequest, *args, **kwargs):
        NewRegisterFormset = formset_factory(
            UserToNewRegisterForm, formset=RequiredFormSet, extra=1
        )
        formset = NewRegisterFormset(prefix=self._usernames_prefix)
        name_form = NewRegisterNameForm(prefix=self._register_name_prefix)
        return render(
            request,
            "rejestrapp/new_register.html",
            {
                "formset": formset,
                "name_form": name_form,
                "back": reverse("rejestrapp:userspace"),
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        NewRegisterFormset = formset_factory(
            UserToNewRegisterForm, formset=RequiredFormSet, extra=1
        )
        formset = NewRegisterFormset(request.POST, prefix=self._usernames_prefix)
        name_form = NewRegisterNameForm(request.POST, prefix=self._register_name_prefix)
        if formset.is_valid() and name_form.is_valid():
            all_users = User.objects.all()
            added_users = []
            added_users_ids = []
            for form in formset:
                try:
                    one_user = all_users.get(username=form.cleaned_data["username"])
                except User.DoesNotExist:
                    return render_error_page(
                        request,
                        "Przynajmniej jeden z wymienionych użytkowników nie istnieje",
                        422,
                        reverse("rejestrapp:new_register"),
                    )
                # The user that made the request is included automatically,
                # Their username shouldn't be among the ones in the form.
                if one_user == request.user or one_user.pk in added_users_ids:
                    return render_error_page(
                        request,
                        "Wpisano tego samego użytkownika wielokrotnie",
                        422,
                        reverse("rejestrapp:new_register"),
                    )
                added_users.append(one_user)
                added_users_ids.append(one_user.pk)
            added_users.append(typing.cast(User, request.user))
            # added_users.append(request.user)
            added_users_ids.append(request.user.pk)
            register = Register.objects.create(name=name_form.cleaned_data["name"])
            register.users.add(*added_users)
            register.save()
            this_users_debt = Debt.objects.get(
                register=register.pk, user=request.user.pk
            )
            this_users_debt.accepted = True
            this_users_debt.save()
            return redirect(reverse("rejestrapp:userspace"))
        else:
            return render_error_page(
                request,
                "Coś się nie zgadzało w Twoim zapytaniu",
                400,
                reverse("rejestrapp:new_register"),
            )


class InviteView(LoginRequiredMixin, View):
    """
    View for displaying the options to accept or reject and invitation.
    """

    http_method_names = ["get", "options"]

    def get(self, request: HttpRequest, *args, **kwargs):
        register, _, error = check_for_errors_in_invite_view(
            request, kwargs["register_id"]
        )
        if error is not None:
            return error
        return render(
            request,
            "rejestrapp/invite.html",
            {"register": register, "back": reverse("rejestrapp:userspace")},
        )


class InviteAcceptView(LoginRequiredMixin, View):
    """
    View for accepting an invitation. When a user is the last one from the
    invited users to accept their invitation, the register's creation is
    finalized and it will start accepting transactions.
    """

    http_method_names = ["post", "options"]

    def post(self, request: HttpRequest, *args, **kwargs):
        register, this_debt, error = check_for_errors_in_invite_view(
            request, kwargs["register_id"]
        )
        if error is not None:
            return error
        this_debt.accepted = True
        this_debt.save()
        all_accepted = True
        for debt in register.debt_set.all():
            if not debt.accepted:
                all_accepted = False
                break
        if all_accepted:
            register.all_accepted = True
            register.save()
        return redirect(reverse("rejestrapp:userspace"))


class InviteRejectView(LoginRequiredMixin, View):
    """
    View for rejecting an invitation. When a single user decides to reject
    their invitation, the register is removed.
    """

    http_method_names = ["post", "options"]

    def post(self, request: HttpRequest, *args, **kwargs):
        register, _, error = check_for_errors_in_invite_view(
            request, kwargs["register_id"]
        )
        if error is not None:
            return error
        for debt in register.debt_set.all():
            debt.delete()
        register.delete()
        return redirect(reverse("rejestrapp:userspace"))
