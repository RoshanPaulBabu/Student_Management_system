from django import forms
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100)

    class Meta:
        model = Student
        exclude = ['roll_number', 'is_approved']
        widgets = {
            'date_of_birth': DateInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
    

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['is_present']        

