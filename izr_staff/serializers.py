# serializers.py

from rest_framework import serializers
from .models import Person, PhoneNumber, EmailAddress, Role


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ["phone_number"]


class EmailAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        fields = ["email"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["role"]


class PersonSerializer(serializers.ModelSerializer):
    phone_numbers = PhoneNumberSerializer(many=True, required=False)
    emails = EmailAddressSerializer(many=True, required=False)
    roles = RoleSerializer(many=True, required=False)

    class Meta:
        model = Person
        fields = ["id", "name", "last_name", "phone_numbers", "emails", "roles"]

    def create(self, validated_data):
        phone_numbers_data = validated_data.pop("phone_numbers", [])
        emails_data = validated_data.pop("emails", [])
        roles_data = validated_data.pop("roles", [])

        person = Person.objects.create(**validated_data)

        for phone_number_data in phone_numbers_data:
            PhoneNumber.objects.create(person=person, **phone_number_data)

        for email_data in emails_data:
            EmailAddress.objects.create(person=person, **email_data)

        for role_data in roles_data:
            Role.objects.create(person=person, **role_data)

        return person

    def update(self, instance, validated_data):
        phone_numbers_data = validated_data.pop("phone_numbers", None)
        emails_data = validated_data.pop("emails", None)
        roles_data = validated_data.pop("roles", None)

        instance.name = validated_data.get("name", instance.name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()

        if phone_numbers_data is not None:
            instance.phone_numbers.all().delete()
            for phone_number_data in phone_numbers_data:
                PhoneNumber.objects.create(person=instance, **phone_number_data)

        if emails_data is not None:
            instance.emails.all().delete()
            for email_data in emails_data:
                EmailAddress.objects.create(person=instance, **email_data)

        if roles_data is not None:
            instance.roles.all().delete()
            for role_data in roles_data:
                Role.objects.create(person=instance, **role_data)

        return instance
