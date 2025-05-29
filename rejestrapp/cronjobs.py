from django.contrib.auth.models import User
from rejestrapp.models import SignupToken


def delete_unfinished_users():
    for token in SignupToken.objects.all():
        User.objects.filter(email=token.email).delete()
        token.delete()


def do_cronjobs():
    cronjobs = [
        delete_unfinished_users,
    ]

    for job in cronjobs:
        job()
