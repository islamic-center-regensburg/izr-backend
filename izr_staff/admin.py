from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Person, PhoneNumber, EmailAddress, Role


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1


class RoleInline(admin.TabularInline):
    model = Role
    extra = 1


class EmailAddressInline(admin.TabularInline):
    model = EmailAddress
    extra = 1


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "last_name")
    search_fields = ("name", "last_name")
    inlines = [RoleInline, PhoneNumberInline, EmailAddressInline]
