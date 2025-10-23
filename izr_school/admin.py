from django.contrib import admin
from .models import Year, Course, Class, CourseDay, Payment, Student, Teacher, Parent


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date")
    search_fields = ("title", "start_date", "end_date")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "course")
    search_fields = ("name", "course__name")


@admin.register(CourseDay)
class CourseDayAdmin(admin.ModelAdmin):
    list_display = ("date", "year")
    search_fields = ("date",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "date_paid", "year")
    search_fields = ("student__first_name", "student__last_name", "year__start_date")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "year", "class_assigned")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "subject",
        "year",
        "class_assigned",
    )
    search_fields = ("first_name", "last_name", "email", "subject")


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "student")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "student__first_name",
        "student__last_name",
    )
