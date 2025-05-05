# Rejestr Składek

[Link do działającej strony](https://frog02-20448.wykr.es/)

Rejestr Składek jest narzędziem przydatnym do rozliczania się ze wspólnych
wydatków w grupie znajomych. Jeśli ktoś często składa się na coś z tymi samymi
ludźmi, to zamiast pilnować kto komu jest indywidualnie winien, można każdemu
liczyć ile wydał i ile dostał, a zadaniem każdego będzie być jak najbliżej zera.

## Jak to działa

### Każdy zaczyna z zerem na koncie

| Imię      | Stan konta |
| --------- | ---------- |
| Róża      | 0          |
| Kalina    | 0          |
| Hiacynt   | 0          |
| Jaskier   | 0          |

Zanim ktokolwiek cokolwiek wyda, każdy jest na zero. Teraz powiedzmy, że
powyźsi znajomi postanowili złożyć się na jedzenie. Zrobili sobie zakupy za
100zł i tym razem Róża zapłaciła za wszystkich. W tej transakcji każdy dostał
coś o wartości 100zł / 4 = 25zł, ale z portfela Róży uszło 100zł, więc na jej
koncie będzie 25zł - 100zł = -75zł. Po tych zakupach ich rejestr prezentuje się
następująco:

| Imię      | Stan konta |
| --------- | ---------- |
| Róża      | -75        |
| Kalina    | 25         |
| Hiacynt   | 25         |
| Jaskier   | 25         |

Jeśli ktoś jest na plusie, to znaczy, że do tej pory dostał więcej niż wydał,
więc na przykład przy następnych zakupach to ta osoba powinna być bardziej
skłonna zapłacić za wszystkich.

Jeśli ktoś jest na minusie, to znaczy, że do tej pory wydał więcej niż dostał,
więc na obecną chwilę może sobie pozwolić na odpoczynek od płacenia za innych.

Teraz powiedzmy, że nasza grupka postanowiła złożyć się na wejście na atrakcję
na festynie. Łącznie bilety za nich wszystkich kosztują 60zł. Płatność gotówką.
Tak się złożyło, że Róża i Kalina nie wzięły swoich portfeli, Hiacynt ma przy
sobie 50zł, a Jaskier ma 10zł. Każdy tutaj otrzymuje coś wartego
60zł / 4 = 15zł, z portfela Hiacynta uszło 50zł (więc zmiana na jego koncie
wyniesie 15zł - 50zł = -35zł), a z portfela Jaskra uszło 10zł
(zmiana 15zł - 10zł = 5zł). Tak wygląda ta sytuacja:

| Imię      | Stan konta przed | Stan konta po | Zmiana |
| --------- | ---------------- | ------------- | ------ |
| Róża      | -75              | -60           | 15     |
| Kalina    | 25               | 40            | 15     |
| Hiacynt   | 25               | 30            | 5      |
| Jaskier   | 25               | -10           | -35    |

Ostatecznie chodzi tu o to, że ile kto dostał, tyle jest mu dodawane, a ile kto
wydał, tyle jest od niego odejmowane. Mając na koncie zero można być pewnym, że
do tej pory wydało się dokładnie tyle, ile się dostało - czy to w formie
jedzenia, jakiejś usługi, czy po prostu przelewu na konto.

## Suma kont jest równa zero

Bardzo istotną właściwością tego rejestru jest to, że w każdym momencie suma
stanów kont wszystkich członków jest równa zero. To odzwierciedla fakt, że jedne
osoby dają drugim jakąś wartość - działa to jak zwykłe pożyczanie pieniędzy, ale
jest dużo wygodniejsze.

## Motywacja i testowanie w boju

Ten projekt powstał po długim czasie obliczania tego rodzaju transakcji ręcznie
w notatkach na telefonie i na kartkach papieru. Wraz z moją grupką znajomych
porządnie przetestowaliśmy ten sposób rozliczania się i jesteśmy z niego bardzo
zadowoleni. Używaliśmy go między innymi do składania się na prezenty
urodzinowe, na wspólne wyjścia, itp. Najdogłębniejszym użyciem tego systemu był
nasz kilkudniowy wyjazd, gdzie każdy posiłek i każdy inny większy wydatek był
zapisywany w tego rodzaju rejestrze. Pojedyńcze transakcje były zapisywane
przeze mnie jako wiadomości do siebie na komunikatorze, a dwa razy w ciągu
wyjazdu przysiedliśmy, żeby podliczyć dotychczas wydane pieniądze, żeby na
koniec wyjazdu nie pomylić się musząc zliczać wszystko ze wszystkich dni naraz.
Zaoszczędziliśmy dużo czasu robiąc to w ten sposób, w przeciwieństwie do tego
jak by to wyglądało, gdyby każdy z nas próbował pilnować ile jest winien każdej
pojedyńczej osobie, i ile każdy jest winien jemu. Widać jednak było, że poszłoby
to wszystko jeszcze szybciej, gdyby obliczenia działy się same i stąd właśnie
przyszedł pomysł na ten projekt.

# Prezentacja

https://github.com/user-attachments/assets/77518663-10d2-4b4b-afe8-258b86ed4e01

# Instrukcja użytkowania

## Rejestracja

Aby założyć konto, potrzebny jest nieużyty wcześniej token rejestracyjny
wygenerowany przez administratora. Czyni to ten system zamkniętym na ludzi
zaproszonych przez właściciela. Niewykluczone, że w przyszłości ten sposób
rejestracji zostanie zastąpiony standardową rejestracją przy użyciu emaila.

## Tworzenie rejestru

Na stronie wyświetlonej po pomyślnym zarejestrowaniu się jest przycisk z napisem
```Stwórz nowy rejestr``` - wciśnij go. Wpisz nazwę rejestru oraz nazwy
użytkowników, których chcesz zaprosić. Zatwierdź. Teraz musisz zaczekać, aż
wszyscy zaproszeni odpowiedzą na zaproszenie. Jeśli wszyscy się zgodzą na
dołączenie, to tworzenie rejestru dobiegnie końca i będzie już można wpisywać
transakcje. Jeśli jednak chociaż jedna osoba odrzuci zaproszenie to tworzenie
rejestru zostanie anulowane. Wtedy można spróbować stworzyć nowy rejestr bez
tej osoby, albo zrobić coś innego odpowiedniego dla konkretnej sytuacji.

## Odpowiadanie na zaproszenia

Na tej samej stronie, na której jest przycisk do tworzenia rejestrów, znajduje
się również lista zaproszeń. Jeśli ktoś wpisał twoją nazwę podczas tworzenia
rejestru, to przyjdzie do ciebie tutaj zaproszenie. Wciśnij ```Odpowiedz```, po
czym wciśnij przycisk odpowiadający temu, co chcesz zrobić - czy przyjąć,
czy nie.

## Tworzenie transakcji

Jak już będziesz członkiem jakiegoś rejestru, wyświetli ci się on w liście
widocznej na wspominanej wcześniej stronie głównej. Wejdź w niego. Masz teraz
dwa sposoby na stworzenie transakcji - manualny i uproszczony.

### Manualna transakcja

Zacznij od wpisania nazwy dla danej transakcji, np. "Pizza", "Kino", "Taxi".
Niżej wpisz o ile mają się zmienić stany konta poszczególnych członków rejestru.
Powinno to wyglądać tak jak we wcześniejszej sekcji -
[Jak to działa](#jak-to-działa). Należy zachować tu zasadę zerowej sumy -
niech wszystkie wpisane wartości dodają się do zera. Jak już wszystko będzie
poprawnie wpisane to zatwierdź przyciskiem znajdującym się na dole. **Uwaga**:
Wpisane wartości nie zostaną dodane do obecnych stanów konta odrazu po
stworzeniu transakcji. O zatwierdzaniu przeczytasz w sekcji
[Głosowanie na transakcję](#głosowanie-na-transakcję) poniżej.

### Uproszczona transakcja

Najpierw wpisz nazwę transakcji. W następne pole wpisz ile kosztowało to, na co
się grupowo składacie. Dalej powpisuj w pola odpowiadające członkom rejestru
jaki był ich dotychczasowy wkład w to co było kupione. Chodzi tu o to, że
zakładamy, że każdy ostatecznie da od siebie tyle samo, tylko że w chwili
kupowania ktoś zapłacił ze swoich pieniędzy za innych i będzie oczekiwał, że
poprzez przyszłe transakcje zostanie mu oddane. Zmiana na czyimś koncie wyniesie
wartość wydatku podzielona na ilość członków rejestru, od której odjęto wkład
tej osoby. Dobrym przykładem tej sytuacji jest podana w sekcji
[Jak to działa](#jak-to-działa) sytuacja z festynem.

## Głosowanie na transakcję

Gdy jakaś transakcja została już wpisana w system, dane z niej nie zostaną
jeszcze dodane do obecnych stanów kont. Najpierw będzie oczekiwała na zgodę
wszystkich członków. Aby wyrazić zgodę, wejdź w daną transakcję ze strony
rejestru, zaznacz pole odpowiadające głosowi, który chciałbyś wysłać i zatwierdź
przyciskiem poniżej. Wartości z transakcji zostaną wliczone w stany kont
użytkowników dopiero gdy wszyscy wyrażą na nią swoją zgodę. Istnieje również
możliwość zagłosowania za usunięciem danej transakcji. **Uwaga**: Transakcję
można usunąć tylko jeśli nie została ona jeszcze zatwierdzona. Po tym, jak
wszyscy wyrazili swoją zgodę, nie można już zmieniać swoich głosów w danej
transakcji. Da się jednocześnie zagłosować za zatwierdzeniem transakcji i za jej
usunięciem. Może to być przydatne np. w sytuacji, gdy ktoś akurat nie
uczestniczył w kupowaniu czegoś (przez co zmiana na jego koncie wyniesie 0)
i ta osoba nie chce przeszkadzać uczestnikom transakcji w głosowaniu za ani za
zatwierdzeniem, ani za usunięciem.

# Przyszły rozwój

Ten projekt będzie się jeszcze rozwijał. Obecnie zaplanowane jest dodanie nowego
rodzaju uproszczonej transakcji, w której można zawrzeć, że jedni w danej
sytuacji dostali więcej niż drudzy - np. zamawiając w restauracji jedna osoba
kupiła zupę za 20zł, a ktoś inny kupił steka za 60zł (wpisanie takiej transakcji
**jest** obecnie możliwe, ale tylko poprzez manualną transakcję, więc trzeba
samemu liczyć ile komu wyjdzie zmiana). Przyda się też lepiej wyglądająca oprawa
graficzna.
