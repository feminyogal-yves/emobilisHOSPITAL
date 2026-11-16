from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from Patients.forms import PatientForm
from Patients.models import Patient
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

# SIGN UP / REGISTRATION

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('dashboard')

    else:
        form = UserCreationForm()

    return render(request, 'index.html', {
        'form': form
    })


# LOGIN

def userlogin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        error_message = 'Invalid username or password.'

    return render(request, 'login.html', {
        'error_message': error_message
    })


# LOGOUT

def logout_view(request):
    if request.method == 'POST':
        logout(request)

    return redirect('login')



# DASHBOARD

@login_required(login_url='login')
def dashboard(request):
    patients = Patient.objects.all()

    return render(request, 'dashboard.html', {
        'patients': patients
    })



# BOOK APPOINTMENT

@login_required(login_url='login')
def bookappointment(request):
    return render(request, 'bookappointment.html')



# PROFILE

@login_required(login_url='login')
def Profile(request):
    return render(request, 'Profile.html')



# ADD PATIENT
@login_required(login_url='login')
def add_patient(request):

    if request.method == 'POST':
        form = PatientForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

    else:
        form = PatientForm()

    return render(request, 'add_patient.html', {
        'form': form
    })


# VIEW PATIENT
@login_required(login_url='login')
def patient_detail(request, pk):

    patient = get_object_or_404(Patient, pk=pk)

    return render(request, 'patient_detail.html', {
        'patient': patient
    })


# EDIT PATIENT

@login_required(login_url='login')
def edit_patient(request, pk):

    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

    else:
        form = PatientForm(instance=patient)

    return render(request, 'add_patient.html', {
        'form': form,
        'patient': patient
    })


# DELETE PATIENT

@login_required(login_url='login')
def delete_patient(request, pk):

    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        patient.delete()
        return redirect('dashboard')

    return render(request, 'patient_confirm_delete.html', {
        'patient': patient
    })

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed