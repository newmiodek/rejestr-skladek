from django.contrib.auth.models import User
from django.db import models


class Register(models.Model):
    name = models.CharField(max_length=128)
    users: models.ManyToManyField = models.ManyToManyField(User, through="Debt")
    all_accepted = models.BooleanField(db_default=False)

    def __str__(self):
        return self.name + " - id: " + str(self.pk)


class Debt(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    register = models.ForeignKey(Register, on_delete=models.PROTECT)
    balance = models.IntegerField(db_default=0)  # w groszach
    accepted = models.BooleanField(db_default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "register"], name="unique_user_register"
            )
        ]

    def __str__(self):
        return f'Stan konta "{self.user.username}" w rejestrze "{self.register.name}"'


class GroupTransaction(models.Model):
    name = models.CharField(max_length=128)
    init_date = models.DateTimeField()
    is_settled = models.BooleanField(db_default=False)
    settle_date = models.DateTimeField(blank=True, null=True)
    debts: models.ManyToManyField = models.ManyToManyField(
        Debt, through="IndividualsTransaction"
    )

    def __str__(self):
        return f"{self.name} - {self.init_date}"


class IndividualsTransaction(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.PROTECT)
    group_transaction = models.ForeignKey(GroupTransaction, on_delete=models.PROTECT)
    amount = models.IntegerField(db_default=0)
    supports = models.BooleanField(db_default=False)
    wants_remove = models.BooleanField(db_default=False)
    balance_before = models.IntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["debt", "group_transaction"],
                name="unique_debt_group_transaction",
            )
        ]

    def __str__(self):
        return f"{self.debt.user.username} {self.debt.register.name} {self.group_transaction.name}"


class SignupToken(models.Model):
    secret = models.CharField(primary_key=True, max_length=64)
    email = models.EmailField(unique=True, blank=False, null=False)

    def __str__(self):
        return "Signup Token"
