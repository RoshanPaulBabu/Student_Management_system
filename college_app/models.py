from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.core.validators import RegexValidator, MinLengthValidator

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    COURSE_CHOICES = (
        ('MCA', 'MCA'),
        ('MBA', 'MBA'),
        ('MMH', 'MMH'),
        ('MA', 'MA'),
        ('MSW', 'MSW'),
        ('MCMS', 'MCMS'),
    )

    name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    email = models.EmailField(max_length=254, unique=True)
    contact = models.CharField(max_length=10, unique=True)
    parent_name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    course = models.CharField(max_length=4, choices=COURSE_CHOICES)
    date_of_birth = models.DateField()
    registration_date = models.DateTimeField(auto_now_add=True)
    student_image = models.ImageField(upload_to='students/images/')
    roll_number = models.CharField(max_length=50, unique=True, blank=True)
    password = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                message="Password should have at least one letter, one number, and one special character"
            )
        ]
    )
    is_approved = models.BooleanField(default=False)

    def clean(self):
        # Don't allow date_of_birth less than 17 years ago.
        if self.date_of_birth > date.today() - timedelta(days=17*365):
            raise ValidationError('Age must be above 17 years.')
        
        if len(self.contact) != 10:
            raise ValidationError('Contact number must have exactly 10 digits.')


    def save(self, *args, **kwargs):
        super(Student, self).save(*args, **kwargs)
        if not self.roll_number:
            self.roll_number = '23SR' + str(self.id)
            super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date}"