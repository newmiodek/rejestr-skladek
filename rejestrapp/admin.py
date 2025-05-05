from django.contrib import admin

from .models import Register, Debt, GroupTransaction, IndividualsTransaction


class DebtInline(admin.StackedInline):
    model = Debt
    extra = 3


class RegisterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name"]}),
    ]
    inlines = [DebtInline]


class IndividualsTransactionInline(admin.StackedInline):
    model = IndividualsTransaction
    extra = 4


class GroupTransactionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "init_date", "is_settled", "settle_date"]}),
    ]
    inlines = [IndividualsTransactionInline]


admin.site.register(Register, RegisterAdmin)
admin.site.register(Debt)
admin.site.register(GroupTransaction, GroupTransactionAdmin)
admin.site.register(IndividualsTransaction)
