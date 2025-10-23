from django.db import models

# Create your models here.
from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return f"{self.name} {self.last_name}"


class PhoneNumber(models.Model):
    person = models.ForeignKey(
        Person, related_name="phone_numbers", on_delete=models.CASCADE
    )
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")

    def __str__(self):
        return f"{self.phone_number} ({self.person.name})"


class EmailAddress(models.Model):
    person = models.ForeignKey(Person, related_name="emails", on_delete=models.CASCADE)
    email = models.EmailField(verbose_name="Email Address")

    def __str__(self):
        return f"{self.email} ({self.person.name})"


class Role(models.Model):
    ROLE_CHOICES = [
        ("staff", "Vorstand"),
        ("manager", "Vertretung"),
        ("admin_schulunterricht", "Schulunterricht"),
        ("admin_frauen", "Frauen"),
        ("admin_entwicklung", "Entwicklung"),
        ("admin_familien_kinder", "Familien & Kinder"),
        ("admin_bestattungen", "Islamische Bestattungen"),
        ("admin_gebaudehalter", "Gebäudehalter"),
        ("admin_hausverwaltung", "Hausverwaltung"),
        ("admin_sport_jugend", "Sport & Jugend"),
    ]

    person = models.ForeignKey(
        "Person", related_name="roles", on_delete=models.CASCADE, verbose_name="Person"
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name="Role")

    def __str__(self):
        return f"{self.get_role_display()} ({self.person.name})"
