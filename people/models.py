from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(null=True, blank=True)
    department = models.CharField(max_length=120, blank=True)
    enrol_no = models.CharField(max_length=80, blank=True)
    joined = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Staff(models.Model):
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(null=True, blank=True)
    department = models.CharField(max_length=120, blank=True)
    staff_id = models.CharField(max_length=80, blank=True)
    joined = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(null=True, blank=True)
    department = models.CharField(max_length=120, blank=True)
    emp_id = models.CharField(max_length=80, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    joined = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
