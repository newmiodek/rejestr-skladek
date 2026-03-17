# Debt Register

[Link to the hosted app](https://frog02-20448.wykr.es/)

Debt Register is a tool that's useful for settling shared expenses with your
friends. If you often buy things as a group, then instead of everyone keeping
track of how much they owe everyone else individually, you can keep track of
how much each person has received, how much they've spent, and everyone's goal
will be to be as close to zero as possible.

## How it works

### Everyone starts with their balance at zero

| Name      | Balance    |
| --------- | ---------- |
| Rose      | 0          |
| Hazel     | 0          |
| Kalina    | 0          |
| Jasmine   | 0          |

Before anyone spends any money, everyone is at zero. Now, let's say, that the
group of friends from the table above decides to go out for dinner. They bought
food for $100 and Rose paid for all of them. In this transaction, everyone got
the equivalent of $100 / 4 = $25, but Rose gave away $100 from her wallet, so
the balance on her account will be $25 - $100 = -$75. After this transaction,
their register looks as follows:

| Name      | Balance    |
| --------- | ---------- |
| Rose      | -75        |
| Hazel     | 25         |
| Kalina    | 25         |
| Jasmine   | 25         |

If someone is above zero, then it means that up to this point they have received
more than they've spent, so next time they decide to buy something together,
that person should feel obliged to pay.

If someone is below zero, then it means that they've spent more than they've
received, so for now they can take a break from paying.

Now let's say that our group of friends decided to buy tickets for a ride at an
amusement park. The tickets cost $60 in total. Cash only. It turned out that
Rose and Hazel left their wallets at home, Jasmine has $50, and Kalina has $10.
Everyone receives the equivalent of $60 / 4 = $15, $50 came out of Jasmine's
wallet (so her balance will change by $15 - $50 = -$35), and $10 came out of
Kalina's wallet (balance will change by $15 - $10 = $5). Here's how it comes
out:

| Name      | Balance before   | Balance after | Change |
| --------- | ---------------- | ------------- | ------ |
| Rose      | -75              | -60           | 15     |
| Hazel     | 25               | 40            | 15     |
| Kalina    | 25               | 30            | 5      |
| Jasmine   | 25               | -10           | -35    |

Ultimately it comes down to the amount of money that someone receives being added
to their balance, and the money they spend being subtracted. If your balance is
at zero, then you can be sure that you got as much as you gave - in the form of
food, some service, or just a plain bank transfer.

## The balances add up to zero

A very important property of a register is the fact that at every moment in
time, if you add up all the balances, you get zero. This represents the fact
that during a transaction some people give some value to others - it works like
borrowing money, but it's simpler to pay everyone back.

## Motivation and field testing

This project began after a long time of doing this type of calculations by hand
in a notes app and on pieces of paper. My friends and I have thoroughly tested
this type of expense settling and we're very happy with it. We've used it for
buying birthday gifts, going out, etc. The most thorough use of this system was
our 10-day trip, where every meal and every other type of expense was recorded
in this type of a register. I wrote down individual transactions as messages to
myself on my phone, and two times during the trip we sat down to add all of it
up, so that at the end of the trip we wouldn't have to add up too much at once,
which we feared would be prone to error. We definitely did end up saving a lot
of time doing it this way in comparison to how long it would have taken us to
keep track of how much each person owes each other person individually, but it
was clear that it would have been even faster to do this with some kind of
automated system. And hence the idea for this project was born.

# Presentation

https://github.com/user-attachments/assets/77518663-10d2-4b4b-afe8-258b86ed4e01

# User's manual

## Creating a register

On the page that you'll see after logging in there is a button with the text
```Stwórz nowy rejestr``` - press it. Enter a name for your register and
usernames of users that you'd like to invite to it. Submit. Now you have to
wait for the users that you've invited to respond to the invitation. If
everyone accepts, the process of creating the register will be over and you
will be able to start using it. If at least one person rejects the invitation,
then the creation of the register will be cancelled.

## Responding to invites

On the same page there is a list of pending invites. Press ```Odpowiedz```,
and then press the button that corresponds to how you want to respond - whether
to accept or reject the invitation.

## Creating transactions

After you become a member of a register you'll see the register in the list
on your main menu. Enter it. Now you have two ways of creating a transaction -
manual and simplified.

### Manual transaction

Start by entering the name of the transaction, for example "Pizza", "Theater",
or "Taxi". Next, enter the amounts by which the balance of each user should
change. It should look like in the [How it works](#how-it-works) section.
You have to respect the zero sum rule - all of the changes have to add up to
zero. After everything has been correctly entered, submit by clicking the
button below. **Notice**: The provided values won't be immediately added to the
balances. To learn about confirming transactions, go to the
[Voting on a transaction](#voting-on-a-transaction) section below.

### Simplified transaction

First, enter the name of the transaction. Then enter the cost of the thing that
you all bought. After that, enter each person's contribution to the payment.
The change in a user's balance will be value of the expense divided by the
number of people in the register minus that user's contribution. An example
of such a transaction is the amusement park situation in the
[How it works](#how-it-works) section.

## Voting on a transaction

When a transaction enters the system, the balance changes that it brings aren't
pushed through right away. It first needs to be accepted by all members of the
register. To accept a transaction go to that transaction's page from the
register's page, check the appropriate checkbox and submit. It's also possible
to vote for a transaction's removal. **Notice**: A transaction can only be
removed if it has not yet been accepted. After everyone voted to accept it,
you can't change your vote on that transaction. It's possible to simultaneously
vote to accept and remove a transaction. It's intended to be done in the case
when someone doesn't care whether a transaction goes through or not, for example
when someone didn't take part in an expense, which means that the change for
them is zero.
