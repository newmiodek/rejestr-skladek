import secrets
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from rejestrapp.models import (
    Debt,
    GroupTransaction,
    IndividualsTransaction,
    Register,
    SignupToken,
)

from .errors import BadGroszeException
from .utils import gr_to_zl


class TestConstants:
    VALID_TRANSACTION_DATA = [
        ("461.79", 46179),
        ("-12.45", -1245),
        ("-371.87", -37187),
        ("342.04", 34204),
        ("-419.51", -41951),
    ]
    NEW_TRANSACTION_NONEXISTENT_USER_MSG = (
        "<p>Przynajmniej jeden z wymienionych użytkowników nie istnieje</p>"
    )
    NEW_TRANSACTION_SAME_USER_MULTIPLE_TIMES_MSG = (
        "<p>Wpisano tego samego użytkownika wielokrotnie</p>"
    )


def post_data_to_new_transaction_view(self, data):
    return self.client.post(
        reverse(
            "rejestrapp:new_transaction", kwargs={"register_id": self.registerA.pk}
        ),
        data=data,
    )


class DontBeLoggedInTests(TestCase):
    """Test the @dont_be_logged_in decorator."""

    def setUp(self):
        """Create two test users and a token for testing successful signup."""
        self.userA = User.objects.create_user(username="userA", password="passwordA")
        self.userB = User.objects.create_user(username="userB", password="passwordB")
        self.secret = secrets.token_hex(32)
        SignupToken.objects.create(secret=self.secret)

    def test_dont_be_logged_in(self):
        """
        When accessing views decorated by @dont_be_logged_in while being logged in
        we should be redirected to the userspace. When trying this while being
        logged out, the page should be shown normally.
        """
        login_data = {"username": "userB", "password": "passwordB"}
        signup_data = {
            "username": "userC",
            "password1": "dj!hd382J",
            "password2": "dj!hd382J",
            "signup_token": self.secret,
        }

        # logged in:
        self.client.force_login(self.userA)

        # GET:
        response = self.client.get(reverse("rejestrapp:login"))
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertEqual(response.content, b"dont_be_logged_in")

        response = self.client.get(reverse("rejestrapp:signup"))
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertEqual(response.content, b"dont_be_logged_in")

        # POST:
        response = self.client.post(reverse("rejestrapp:login"), data=login_data)
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertEqual(response.content, b"dont_be_logged_in")

        response = self.client.post(reverse("rejestrapp:signup"), data=signup_data)
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertEqual(response.content, b"dont_be_logged_in")

        # logged out:
        self.client.logout()

        # GET:
        response = self.client.get(reverse("rejestrapp:login"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("rejestrapp:signup"))
        self.assertEqual(response.status_code, 200)

        # POST
        response = self.client.post(reverse("rejestrapp:login"), data=login_data)
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertEqual(response.content, b"")

        self.client.logout()
        response = self.client.post(reverse("rejestrapp:signup"), data=signup_data)
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertEqual(response.content, b"")


class FunctionUtilsTests(SimpleTestCase):
    """Test regular functions from utils."""

    def test_gr_to_zl_edge_cases(self):
        """Check all edge cases and cases in between."""
        pairs = [
            (120, "1.20"),
            (100, "1.00"),
            (99, "0.99"),
            (87, "0.87"),
            (10, "0.10"),
            (9, "0.09"),
            (6, "0.06"),
            (1, "0.01"),
            (0, "0.00"),
            (-1, "-0.01"),
            (-4, "-0.04"),
            (-9, "-0.09"),
            (-10, "-0.10"),
            (-28, "-0.28"),
            (-99, "-0.99"),
            (-100, "-1.00"),
            (-4444, "-44.44"),
        ]
        for pair in pairs:
            self.assertEqual(gr_to_zl(pair[0]), pair[1])

    def test_gr_to_zl_non_int_gr(self):
        """
        Trying to convert a non-integer value
        should result in a BadGroszeException being raised.
        """
        self.assertRaises(BadGroszeException, gr_to_zl, gr=123.4)
        self.assertRaises(BadGroszeException, gr_to_zl, gr=-34.0)


class CheckIfCanBeViewedTests(TestCase):
    """Test the @check_if_can_be_viewed decorator"""

    def setUp(self):
        """
        Initialize 3 users and 2 registers.
        A and B belong to registerA, which has all_accepted = True
        B and C belong to registerB, which has all_accepted = False
        """
        self.userA = User.objects.create_user(username="userA", password="passwordA")
        self.userB = User.objects.create_user(username="userB", password="passwordB")
        self.userC = User.objects.create_user(username="userC", password="passwordC")

        self.registerA = Register.objects.create(name="registerA", all_accepted=True)
        self.registerA.users.add(
            self.userA, self.userB, through_defaults={"accepted": True}
        )

        self.registerB = Register.objects.create(name="registerB", all_accepted=False)
        self.registerB.users.add(
            self.userB, self.userC, through_defaults={"accepted": False}
        )

        self.group_transactionA = GroupTransaction.objects.create(
            name="group_transactionA", init_date=timezone.now()
        )
        for debt in Debt.objects.filter(register=self.registerA.pk):
            self.group_transactionA.debts.add(debt)

        self.not_your_register_message = "<p>Nie jesteś członkiem tego rejestru</p>"
        self.not_accepted_message = (
            "<p>Ten rejestr jeszcze nie został "
            "zaakceptowany przez wszystkich zaproszonych</p>"
        )

    def try_your_register(self, reversing_str, reverse_kwargs, post_data):
        """
        If you belong to the register you're trying to access,
        and the register has been accepted by all invited users,
        then it should be displayed without issue.
        userA belongs to registerA, which is accepted.
        """
        self.client.force_login(self.userA)
        reverse_kwargs.update({"register_id": self.registerA.pk})
        response = self.client.get(reverse(reversing_str, kwargs=reverse_kwargs))
        self.assertEqual(response.status_code, 200)

        if post_data is not None:
            response = self.client.post(
                reverse(reversing_str, kwargs=reverse_kwargs), data=post_data
            )
            self.assertEqual(response.status_code, 302)

    def try_not_your_register(self, reversing_str, reverse_kwargs, post_data):
        """
        If you DON'T belong to the register you're trying to access,
        then an appropriate error message should be displayed
        instead of the register's page.
        userC doesn't belong to registerA, which is accepted.
        """
        self.client.force_login(self.userC)
        reverse_kwargs.update({"register_id": self.registerA.pk})
        response = self.client.get(reverse(reversing_str, kwargs=reverse_kwargs))
        self.assertEqual(response.status_code, 403)
        self.assertInHTML(
            self.not_your_register_message,
            response.content.decode(),
        )

        if post_data is not None:
            response = self.client.post(
                reverse(reversing_str, kwargs=reverse_kwargs), data=post_data
            )
            self.assertEqual(response.status_code, 403)
            self.assertInHTML(
                self.not_your_register_message,
                response.content.decode(),
            )

    def try_not_accepted_register(self, reversing_str, reverse_kwargs, post_data):
        """
        If you DO belong to a register, but it has not yet been accepted
        by all invited users, you should see an appropriate message
        instead of the register's page when you try to access it.
        userB belongs to registerB, which is not accepted.
        """
        self.client.force_login(self.userB)
        reverse_kwargs.update({"register_id": self.registerB.pk})
        response = self.client.get(reverse(reversing_str, kwargs=reverse_kwargs))
        self.assertEqual(response.status_code, 403)
        self.assertInHTML(
            self.not_accepted_message,
            response.content.decode(),
        )

        if post_data is not None:
            response = self.client.post(
                reverse(reversing_str, kwargs=reverse_kwargs), data=post_data
            )
            self.assertEqual(response.status_code, 403)
            self.assertInHTML(
                self.not_accepted_message,
                response.content.decode(),
            )

    def try_not_accepted_and_not_your_register(
        self, reversing_str, reverse_kwargs, post_data
    ):
        """
        If you neither belong to a register, nor is the register accepted,
        then only the error message saying that you don't belong here
        should be displayed when you try to access it.
        userA doesn't belong to registerB, which is not accepted.
        """
        self.client.force_login(self.userA)
        reverse_kwargs.update({"register_id": self.registerB.pk})
        response = self.client.get(reverse(reversing_str, kwargs=reverse_kwargs))
        self.assertEqual(response.status_code, 403)
        self.assertInHTML(
            self.not_your_register_message,
            response.content.decode(),
        )

        if post_data is not None:
            response = self.client.post(
                reverse(reversing_str, kwargs=reverse_kwargs), data=post_data
            )
            self.assertEqual(response.status_code, 403)
            self.assertInHTML(
                self.not_your_register_message,
                response.content.decode(),
            )

    def test_check_if_can_be_viewed(self):
        """
        Check if the views protected by
        the @check_if_can_be_viewed decorator
        are being protected properly.
        """
        # each tuple in this list has the following format:
        # (
        #     string_that_reverses_to_a_view,
        #     kwargs other than "register_id" needed by the view's urlconf,
        #     data to POST to a view, or None if a view only GETs
        # )
        views_to_check = [
            (
                "rejestrapp:register",
                {},
                None,
            ),
            (
                "rejestrapp:new_transaction",
                {},
                {
                    "transaction_name": "group_transactionB",
                    f"value_for_{self.userA.pk}": "67.42",
                    f"value_for_{self.userB.pk}": "-67.42",
                },
            ),
            (
                "rejestrapp:new_easy_transaction",
                {},
                {
                    "transaction_name": "group_transactionB",
                    "expense": "412.79",
                    f"value_for_{self.userA.pk}": "309.50",
                    f"value_for_{self.userB.pk}": "103.29",
                },
            ),
            (
                "rejestrapp:transaction_vote",
                {"group_transaction_id": self.group_transactionA.pk},
                {"supports": True, "wants_remove": False},
            ),
        ]

        for view_to_check in views_to_check:
            self.try_your_register(*view_to_check)
            self.try_not_your_register(*view_to_check)
            self.try_not_accepted_register(*view_to_check)
            self.try_not_accepted_and_not_your_register(*view_to_check)


class SignUpViewTests(TestCase):
    def setUp(self):
        self.secret = secrets.token_hex(32)
        self.signup_data = {
            "username": "userA",
            "password1": "akeugr!2364t9JVFCTH",
            "password2": "akeugr!2364t9JVFCTH",
            "signup_token": self.secret,
        }
        SignupToken.objects.create(secret=self.secret)

    def test_user_automatically_authenticated_after_signup(self):
        """
        If the server's response sets a sessionid,
        and if that sessionid is associated with the user
        that was just created through the signup view,
        then the person creating the user account won't
        have to log in because they will be logged in automatically.
        """
        response = self.client.post(
            reverse("rejestrapp:signup"),
            data=self.signup_data,
        )
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertNotEqual(self.client.session.items(), {}.items())
        userid = self.client.session["_auth_user_id"]
        username = User.objects.get(pk=userid).username
        self.assertEqual(username, "userA")

    def test_signup_with_nonexistent_token_fails(self):
        """
        If a user supplies a token that is NOT one of the tokens
        in the database, then the signup should fail.
        """
        bad_token = self.secret
        if bad_token[0] == "0":
            bad_token = "1" + bad_token[1:]
        else:
            bad_token = "0" + bad_token[1:]
        self.signup_data["signup_token"] = bad_token
        response = self.client.post(
            reverse("rejestrapp:signup"),
            data=self.signup_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.items(), {}.items())

    def test_signup_with_used_token_fails(self):
        """
        If a user supplies a token that has already
        been used, then the signup should fail.
        """
        token = SignupToken.objects.first()
        token.used_up = True
        token.save()
        response = self.client.post(
            reverse("rejestrapp:signup"),
            data=self.signup_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.items(), {}.items())


class NewTransactionTests(TestCase):
    def setUp(self):
        """
        5 users in 1 register
        """
        users = ["A", "B", "C", "D", "E"]
        self.users = [User.objects.create_user(username=u, password=u) for u in users]
        self.registerA = Register.objects.create(name="registerA", all_accepted=True)
        self.registerA.users.add(*self.users, through_defaults={"accepted": True})
        self.client.force_login(self.users[0])

    def test_new_transaction_post_creates_transactions(self):
        """
        POSTing valid data to the new transaction view should result
        in a GroupTransaction object being created, as well as
        appropriate IndividualsTransaction objects.
        """
        data = {
            f"value_for_{d.user.pk}": "0"
            for d in Debt.objects.filter(register=self.registerA)
        }
        data.update({"transaction_name": "transactionA"})

        self.assertEqual(GroupTransaction.objects.count(), 0)
        self.assertEqual(IndividualsTransaction.objects.count(), 0)
        response = post_data_to_new_transaction_view(self, data)
        self.assertEqual(GroupTransaction.objects.count(), 1)
        self.assertEqual(IndividualsTransaction.objects.count(), 5)
        self.assertRedirects(
            response,
            reverse(
                "rejestrapp:transaction_vote",
                kwargs={
                    "register_id": self.registerA.pk,
                    "group_transaction_id": GroupTransaction.objects.first().pk,
                },
            ),
        )
        for indiv in IndividualsTransaction.objects.all():
            self.assertFalse(indiv.supports)
            self.assertFalse(indiv.wants_remove)

    def test_new_transaction_checks_if_values_add_up_to_zero(self):
        """
        The new transaction view should check whether the supplied values
        add up to zero and not create any transactions when they don't.
        """
        # adds up to 50.0 --> invalid
        data = {f"value_for_{self.users[i].pk}": "10.0" for i in range(0, 5)}
        data.update({"transaction_name": "transactionA"})
        response = post_data_to_new_transaction_view(self, data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(GroupTransaction.objects.count(), 0)
        self.assertEqual(IndividualsTransaction.objects.count(), 0)

        # adds up to 0.0 --> valid
        data = {
            f"value_for_{self.users[i].pk}": TestConstants.VALID_TRANSACTION_DATA[i][0]
            for i in range(0, 5)
        }
        data.update({"transaction_name": "transactionB"})
        response = post_data_to_new_transaction_view(self, data)
        self.assertEqual(GroupTransaction.objects.count(), 1)
        self.assertEqual(IndividualsTransaction.objects.count(), 5)
        self.assertRedirects(
            response,
            reverse(
                "rejestrapp:transaction_vote",
                kwargs={
                    "register_id": self.registerA.pk,
                    "group_transaction_id": GroupTransaction.objects.first().pk,
                },
            ),
        )

    def test_new_transaction_converts_input_values_to_gr(self):
        """
        The values this view receives are quantities in zloty as strings
        and they should be properly converted to grosze as integers.
        """
        data = {
            f"value_for_{self.users[i].pk}": TestConstants.VALID_TRANSACTION_DATA[i][0]
            for i in range(0, 5)
        }
        data.update({"transaction_name": "transactionA"})
        post_data_to_new_transaction_view(self, data)
        IndividualsTransaction.objects.all()
        for i in range(0, 5):
            self.assertEqual(
                IndividualsTransaction.objects.get(debt__user=self.users[i].pk).amount,
                TestConstants.VALID_TRANSACTION_DATA[i][1],
            )


class TransactionVoteViewTests(TestCase):
    def setUp(self):
        """
        5 users in 1 register, 1 transaction with valid data and default votes
        """
        users = ["A", "B", "C", "D", "E"]
        self.users = [User.objects.create_user(username=u, password=u) for u in users]
        self.registerA = Register.objects.create(name="registerA", all_accepted=True)
        self.registerA.users.add(*self.users, through_defaults={"accepted": True})
        self.transaction_data = {
            f"value_for_{self.users[i].pk}": TestConstants.VALID_TRANSACTION_DATA[i][0]
            for i in range(0, 5)
        }
        self.transaction_data.update({"transaction_name": "transactionA"})
        self.client.force_login(self.users[0])
        post_data_to_new_transaction_view(self, self.transaction_data)
        self.url = reverse(
            "rejestrapp:transaction_vote",
            kwargs={
                "register_id": self.registerA.pk,
                "group_transaction_id": GroupTransaction.objects.first().pk,
            },
        )

    def test_supporting_non_final_indiv(self):
        """
        When a user declares their support for a transaction,
        but they're not the last one to do so, then the only thing
        that should happen is the 'supports' option for their indiv
        should become True - nothing more.
        """
        data = {"supports": True, "wants_remove": False}
        for indiv in IndividualsTransaction.objects.all():
            self.assertFalse(indiv.supports)
            self.assertEqual(indiv.debt.balance, 0)
        transaction = GroupTransaction.objects.first()
        self.assertFalse(transaction.is_settled)
        self.assertEqual(transaction.settle_date, None)

        self.client.post(self.url, data=data)

        for indiv in IndividualsTransaction.objects.all():
            self.assertEqual(indiv.debt.balance, 0)
            if indiv.debt.user.pk == self.users[0].pk:
                self.assertTrue(indiv.supports)
            else:
                self.assertFalse(indiv.supports)
        transaction = GroupTransaction.objects.first()
        self.assertFalse(transaction.is_settled)
        self.assertEqual(transaction.settle_date, None)

    def test_supporting_final_indiv(self):
        """
        When a user declares their support for a transaction,
        and they're the last one to do so, then the group transaction
        should be marked as settled, the debts' balance values should
        be updated, and indivs should get their 'balance_before' values set.
        """
        data = {"supports": True, "wants_remove": False}
        IndividualsTransaction.objects.exclude(debt__user=self.users[0].pk).update(
            supports=True
        )
        for indiv in IndividualsTransaction.objects.all():
            self.assertEqual(indiv.debt.balance, 0)
            self.assertEqual(indiv.balance_before, None)

        self.client.post(self.url, data=data)

        for i in range(0, 5):
            indiv = IndividualsTransaction.objects.get(debt__user=self.users[i].pk)
            self.assertEqual(
                indiv.debt.balance, TestConstants.VALID_TRANSACTION_DATA[i][1]
            )
            self.assertTrue(indiv.supports)
            self.assertEqual(indiv.balance_before, 0)
        transaction = GroupTransaction.objects.first()
        self.assertTrue(transaction.is_settled)
        self.assertNotEqual(transaction.settle_date, None)

    def test_wanting_remove_non_final_indiv(self):
        """
        When a user declares that they want to remove a transaction,
        but they're not the last one to do so, then the only thing
        that should happen is the 'wants_remove' option for their indiv
        should become True - nothing more.
        """
        data = {"supports": False, "wants_remove": True}
        for indiv in IndividualsTransaction.objects.all():
            self.assertFalse(indiv.wants_remove)
        self.assertEqual(GroupTransaction.objects.count(), 1)
        self.assertEqual(IndividualsTransaction.objects.count(), 5)

        self.client.post(self.url, data=data)

        for indiv in IndividualsTransaction.objects.all():
            if indiv.debt.user.pk == self.users[0].pk:
                self.assertTrue(indiv.wants_remove)
            else:
                self.assertFalse(indiv.wants_remove)
        self.assertEqual(GroupTransaction.objects.count(), 1)
        self.assertEqual(IndividualsTransaction.objects.count(), 5)

    def test_wanting_remove_final_indiv(self):
        """
        When a user declares that they want to remove a transaction,
        and they're the last one to do so, then the group transaction object
        and its associated indivs should be removed - no other effects.
        """
        data = {"supports": False, "wants_remove": True}
        IndividualsTransaction.objects.exclude(debt__user=self.users[0].pk).update(
            wants_remove=True
        )
        self.assertEqual(GroupTransaction.objects.count(), 1)
        self.assertEqual(IndividualsTransaction.objects.count(), 5)

        self.client.post(self.url, data=data)

        self.assertEqual(GroupTransaction.objects.count(), 0)
        self.assertEqual(IndividualsTransaction.objects.count(), 0)

    def test_remove_when_both_supported_and_wanted_removed_by_all(self):
        """
        When a user simultaneously gives support and wants remove,
        and all other users have also done so, then removing
        the transaction should take priority.
        """
        data = {"supports": True, "wants_remove": True}
        IndividualsTransaction.objects.exclude(debt__user=self.users[0].pk).update(
            supports=True, wants_remove=True
        )
        self.assertEqual(GroupTransaction.objects.count(), 1)
        self.assertEqual(IndividualsTransaction.objects.count(), 5)

        self.client.post(self.url, data=data)

        self.assertEqual(GroupTransaction.objects.count(), 0)
        self.assertEqual(IndividualsTransaction.objects.count(), 0)


class NewRegisterViewTests(TestCase):
    def setUp(self):
        """
        5 users, form data for creating a register, logged in as 'A'.
        """
        self.data = {
            "usernames-TOTAL_FORMS": "4",
            "usernames-INITIAL_FORMS": "0",
            "usernames-MIN_NUM_FORMS": "0",
            "usernames-MAX_NUM_FORMS": "1000",
            "register_name-name": "registerA",
            "usernames-0-username": "B",
            "usernames-1-username": "C",
            "usernames-2-username": "D",
            "usernames-3-username": "E",
        }
        users = ["A", "B", "C", "D", "E"]
        self.users = [User.objects.create_user(username=u, password=u) for u in users]
        self.client.force_login(self.users[0])

    def check_422(self, response, msg):
        self.assertEqual(Register.objects.count(), 0)
        self.assertEqual(response.status_code, 422)
        self.assertInHTML(msg, response.content.decode())

    def test_new_register_view(self):
        """
        Test basic correct creation of a new register.
        """
        self.assertEqual(Register.objects.count(), 0)

        self.client.post(reverse("rejestrapp:new_register"), data=self.data)

        self.assertEqual(Register.objects.count(), 1)
        register = Register.objects.first()
        self.assertFalse(register.all_accepted)
        self.assertEqual(register.users.count(), len(self.users))
        for i, debt in enumerate(register.debt_set.all().order_by("user__username")):
            self.assertEqual(debt.user, self.users[i])
            if debt.user == self.users[0]:
                self.assertTrue(debt.accepted)
            else:
                self.assertFalse(debt.accepted)

    def test_new_register_nonexistent_user_case(self):
        """
        The view should display an error and not create any registers
        when one or more of the supplied users doesn't exist.
        """
        self.data["usernames-3-username"] = "F"

        response = self.client.post(reverse("rejestrapp:new_register"), data=self.data)

        self.check_422(response, TestConstants.NEW_TRANSACTION_NONEXISTENT_USER_MSG)

    def test_new_register_deny_when_user_supplies_themself(self):
        """
        The view should display an error and not create any registers
        when the user submitting the form supplied their own account.
        """
        self.data["usernames-3-username"] = "A"

        response = self.client.post(reverse("rejestrapp:new_register"), data=self.data)

        self.check_422(
            response, TestConstants.NEW_TRANSACTION_SAME_USER_MULTIPLE_TIMES_MSG
        )

    def test_new_register_deny_when_one_user_multiple_times(self):
        """
        The view should display an error and not create any registers
        when the user submitting the form supplied one user more than once.
        """
        self.data["usernames-3-username"] = "D"

        response = self.client.post(reverse("rejestrapp:new_register"), data=self.data)

        self.check_422(
            response, TestConstants.NEW_TRANSACTION_SAME_USER_MULTIPLE_TIMES_MSG
        )


class InviteTests(TestCase):
    def setUp(self):
        """
        5 users, 1 register being created.
        """
        users = ["A", "B", "C", "D", "E"]
        self.users = [User.objects.create_user(username=u, password=u) for u in users]
        self.registerA = Register.objects.create(name="registerA", all_accepted=False)
        self.registerA.users.add(*self.users, through_defaults={"accepted": False})

    def test_invite_accept_non_final(self):
        """
        Test correctly accepting an invitation
        when the user is NOT the last one to do so.
        """
        self.client.force_login(self.users[0])
        response = self.client.post(
            reverse(
                "rejestrapp:invite_accept", kwargs={"register_id": self.registerA.pk}
            )
        )
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertFalse(Register.objects.first().all_accepted)

    def test_invite_accept_final(self):
        """
        Test correctly accepting an invitation
        when the user IS the last one to do so.
        """
        for debt in Debt.objects.exclude(user=self.users[0].pk):
            debt.accepted = True
            debt.save()

        self.client.force_login(self.users[0])
        response = self.client.post(
            reverse(
                "rejestrapp:invite_accept", kwargs={"register_id": self.registerA.pk}
            )
        )
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertTrue(Register.objects.first().all_accepted)

    def test_invite_accept_not_invited(self):
        """
        The view should display an error message
        when an uninvited user tries to POST.
        """
        uninvited_user = User.objects.create_user(username="F", password="F")
        self.client.force_login(uninvited_user)
        response = self.client.post(
            reverse(
                "rejestrapp:invite_accept", kwargs={"register_id": self.registerA.pk}
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertInHTML(
            "<p>Nie zaproszono Cie do tego rejestru</p>", response.content.decode()
        )

    def test_invite_accept_already_accepted(self):
        """
        The view should display an error message
        when a user that already accepted their invitation
        tries to accept it again.
        """
        self.client.force_login(self.users[0])
        self.client.post(
            reverse(
                "rejestrapp:invite_accept", kwargs={"register_id": self.registerA.pk}
            )
        )
        response = self.client.post(
            reverse(
                "rejestrapp:invite_accept", kwargs={"register_id": self.registerA.pk}
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertInHTML(
            "<p>Już zaakceptowałeś/aś to zaproszenie</p>", response.content.decode()
        )

    def test_invite_reject(self):
        """
        When even a single user rejects their invitation to a register,
        the register should be deleted.
        """
        self.client.force_login(self.users[0])
        response = self.client.post(
            reverse(
                "rejestrapp:invite_reject", kwargs={"register_id": self.registerA.pk}
            )
        )
        self.assertRedirects(response, reverse("rejestrapp:userspace"))
        self.assertEqual(Debt.objects.count(), 0)
        self.assertEqual(Register.objects.count(), 0)
