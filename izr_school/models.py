from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Year(models.Model):
    title = models.CharField(max_length=255, default="")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.start_date.year} - {self.end_date.year}"


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, related_name="classes", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class CourseDay(models.Model):
    date = models.DateField()
    year = models.ForeignKey(Year, related_name="course_days", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - {self.year}"


class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Fields to relate to Year, Course, and Class
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    class_assigned = models.ForeignKey(
        Class, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        abstract = True


class Student(Person):
    enrollment_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Teacher(Person):
    subject = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"


class Parent(Person):
    student = models.ForeignKey(
        Student, related_name="parents", on_delete=models.CASCADE
    )

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name} - Parent of {self.student.first_name}"
        )


class Payment(models.Model):
    student = models.ForeignKey(
        Student, related_name="payments", on_delete=models.CASCADE
    )  # Now directly related to Student
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date_paid = models.DateField(default=timezone.now)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)

    def __str__(self):
        return f"Payment of {self.amount} by {self.student} for {self.year}"
