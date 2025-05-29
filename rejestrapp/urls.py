from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "rejestrapp"
urlpatterns = [
    path("", views.UserspaceView.as_view(), name="userspace"),
    path(
        "login/",
        views.NoRepeatLoginView.as_view(template_name="rejestrapp/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path(
        "account-activation/<slug:token>/",
        views.AccountActivationView.as_view(),
        name="account_activation",
    ),
    path(
        "account-activation-cancelling/<slug:token>/",
        views.AccountActivationCancelView.as_view(),
        name="account_activation_cancelling",
    ),
    path("new-register/", views.NewRegisterView.as_view(), name="new_register"),
    path("register/<int:register_id>/", views.RegisterView.as_view(), name="register"),
    path(
        "register/<int:register_id>/new-transaction/",
        views.NewTransactionView.as_view(),
        name="new_transaction",
    ),
    path(
        "register/<int:register_id>/new-easy-transaction/",
        views.NewEasyTransactionView.as_view(),
        name="new_easy_transaction",
    ),
    path(
        "register/<int:register_id>/transaction/<int:group_transaction_id>/",
        views.TransactionVoteView.as_view(),
        name="transaction_vote",
    ),
    path("invite/<int:register_id>/", views.InviteView.as_view(), name="invite"),
    path(
        "invite/<int:register_id>/accept/",
        views.InviteAcceptView.as_view(),
        name="invite_accept",
    ),
    path(
        "invite/<int:register_id>/reject/",
        views.InviteRejectView.as_view(),
        name="invite_reject",
    ),
]
