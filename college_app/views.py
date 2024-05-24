from django.shortcuts import render, redirect , get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm





# Create your views here.
def index(request):
    return render (request,'index.html')

def about(request):
    return render (request,'about.html')


def register(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = StudentForm()

    return render(request, 'register.html', {'form': form})

def thanks(request):
    return render(request, 'thanks.html')


def approval(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        action = request.POST['action']
        student = Student.objects.get(id=student_id)

        if action == 'approve':
            student.is_approved = True
            student.save()

            # Send an email to the student
            send_mail(
                'Your registration has been approved',
                'Your User Name is {} and your password is {}.'.format(student.roll_number, student.password),
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )

        elif action == 'reject':
            student.delete()

    students = Student.objects.filter(is_approved=False)
    return render(request, 'approval.html', {'students': students})

def student_detail(request, student_id):
    student = Student.objects.get(id=student_id)

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'approve':
            student.is_approved = True
            student.save()

            send_mail(
                'Your registration has been approved',
                'Your User Name is {} and your password is {}.'.format(student.roll_number, student.password),
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )
            return redirect('approval')

        elif action == 'reject':
            student.delete()
            return redirect('approval')

    return render(request, 'student_detail.html', {'student': student})
 



def mark_attendance(request):
    students = Student.objects.filter(is_approved=True)
    date = request.POST.get('date')
    attendance_marked = Attendance.objects.filter(date=date).exists()

    if request.method == 'POST' and not attendance_marked:
        for student in students:
            is_present = request.POST.get(student.roll_number) == 'Present'
            Attendance.objects.create(student=student, date=date, is_present=is_present)
    return render(request, 'mark_attendance.html', {'students': students,'attendance_marked': attendance_marked})



   
def staff_dashboard(request):
    students = Student.objects.filter(is_approved=True)
    student_attendance = []
    for student in students:
        total_present = Attendance.objects.filter(student=student, is_present=True).count()
        total_absent = Attendance.objects.filter(student=student, is_present=False).count()
        total = total_present + total_absent
        if total > 0:
            percentage = round((total_present / total) * 100)
        else:
            percentage = 0
        student_attendance.append((student, total_present, total_absent, percentage))
    return render(request, 'staff_dashboard.html', {'student_attendance': student_attendance})




def student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendances = Attendance.objects.filter(student=student)
    total_present = attendances.filter(is_present=True).count()
    total_absent = attendances.filter(is_present=False).count()
    return render(request, 'student_view.html', {'student': student, 'total_present': total_present, 'total_absent': total_absent, 'attendances': attendances})


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('students_list')
    return render(request, 'confirm_delete.html', {'student': student})

def attendance_details(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        attendances = Attendance.objects.filter(date=date)
        present_students = [attendance.student for attendance in attendances if attendance.is_present]
        absent_students = [attendance.student for attendance in attendances if not attendance.is_present]
    else:
        date = request.GET.get('date')
        if date:
            attendances = Attendance.objects.filter(date=date)
            present_students = [attendance.student for attendance in attendances if attendance.is_present]
            absent_students = [attendance.student for attendance in attendances if not attendance.is_present]
        else:
            attendances = []
            present_students = []
            absent_students = []
    return render(request, 'attendance_details.html', {'present_students': present_students, 'absent_students': absent_students, 'date': date})



def edit_attendance(request, date):
    attendances = Attendance.objects.filter(date=date)
    if request.method == 'POST':
        for attendance in attendances:
            form = AttendanceForm(request.POST, instance=attendance, prefix=str(attendance.id))
            if form.is_valid():
                form.save()
        return redirect('attendance_details')
    else:
        forms = [AttendanceForm(instance=attendance, prefix=str(attendance.id)) for attendance in attendances]
    return render(request, 'edit_attendance.html', {'forms': forms, 'date': date})

def student_dashboard(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    total_present = Attendance.objects.filter(student=student, is_present=True).count()
    total_absent = Attendance.objects.filter(student=student, is_present=False).count()
    total = total_present + total_absent
    if total > 0:
        percentage = round((total_present / total) * 100)
    else:
        percentage = 0
    return render(request, 'student_dashboard.html', {'student': student, 'total_present': total_present, 'total_absent': total_absent, 'percentage': percentage})


class s_student_detail(UpdateView):
    model = Student
    fields = ['name', 'email','contact', 'parent_name', 'gender', 'date_of_birth', 'student_image'] 
    template_name = 's_student_detail.html'

    def get_success_url(self):
        return reverse_lazy('student_dashboard', kwargs={'student_id': self.object.id})


def s_attendance_detail(request, student_id):
    # get the student object by id
    student = get_object_or_404(Student, id=student_id)
    # get the attendance queryset and sort it by date
    attendances = Attendance.objects.filter(student=student).order_by('date')
    total_present = attendances.filter(is_present=True).count()
    total_absent = attendances.filter(is_present=False).count()
    total = total_present + total_absent
    if total > 0:
        percentage = round((total_present / total) * 100)
    else:
        percentage = 0
    # pass the sorted attendances to the template context
    context = {
        'student': student,
        'attendances': attendances,
        'total_present': total_present,
        'total_absent': total_absent,
        'percentage': percentage,
    }
    return render(request, 's_attendance_detail.html', context)

def st_attendance_detail(request, student_id):
    # get the student object by id
    student = get_object_or_404(Student, id=student_id)
    # get the attendance queryset and sort it by date
    attendances = Attendance.objects.filter(student=student).order_by('date')
    total_present = attendances.filter(is_present=True).count()
    total_absent = attendances.filter(is_present=False).count()
    total = total_present + total_absent
    if total > 0:
        percentage = round((total_present / total) * 100)
    else:
        percentage = 0
    # pass the sorted attendances to the template context
    context = {
        'student': student,
        'attendances': attendances,
        'total_present': total_present,
        'total_absent': total_absent,
        'percentage': percentage,
    }
    return render(request, 'st_attendance_detail.html', context)



def student_login(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(roll_number=roll_number, password=password)
            if not student.is_approved:
                messages.error(request, "Your account has not been approved yet. Please contact the administrator.")
                return render(request, 'login.html')
            # Redirect to a profile page or any other page after successful login
            # For now, redirecting to a success message
            return redirect('student_dashboard', student_id=student.id)  # Replace 'success_page' with your desired URL name
        except Student.DoesNotExist:
            messages.error(request, "Invalid roll number or password. Please try again.")

    return render(request, 'login.html')


def students_list(request):
    students = Student.objects.filter(is_approved=True)
    return render(request, 'students_list.html', {'students': students})

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('staff_dashboard')
            else:
                return render(request, 'admin_login.html', {'form': form, 'error_message': 'Invalid credentials'})

    else:
        form = AuthenticationForm()

    return render(request, 'admin_login.html', {'form': form})