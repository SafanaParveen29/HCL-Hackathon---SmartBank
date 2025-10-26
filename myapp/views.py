from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import*
import re
from django.db.models import Q
import random

def UserRegister(request):
    if request.method == "POST":
        Password = request.POST.get("Password")
        Confirm_Password = request.POST.get("Confirm_Password")
        if Password == Confirm_Password:
            First_Name = request.POST.get('First_Name')
            Last_Name = request.POST.get('Last_Name')
            Mobile = request.POST.get('Mobile')
            Email = request.POST.get('Email')
            Aadhar_Number = request.POST.get('Aadhar_Number')
            DOB = request.POST.get('DOB')
            Address = request.POST.get('Address')
            
            phone_pattern = re.compile(r'^\d{10}$')  
            if not phone_pattern.match(Mobile):
                messages.error(request, "Enter a valid mobile number")
                return redirect('UserRegister')

            existing = UserProfile.objects.filter(Q(Mobile=Mobile) | Q(Email=Email))
            if existing.exists():
                messages.error(request, "User with this Mobile or Email already exists")
                return redirect('UserRegister')
            
            customer = UserProfile.objects.create(
                First_Name=First_Name, 
                Last_Name=Last_Name, 
                Mobile=Mobile, 
                Email=Email, 
                Aadhar_Number=Aadhar_Number, 
                DOB=DOB,
                Address=Address,
                Password=Password,
                KYC_status = 'Not_Updated',
                Status = 'Pending',
                )
            
            if customer:
                messages.success(request, "User profile has been registered successfully! Update your KYC")
                return redirect('KYC_update')
    return render(request, 'UserRegister.html')

def KYC_update(request):
    if request.method == "POST":
        Mobile = request.POST.get('Mobile')
        Aadhar_Number = request.POST.get('Aadhar_Number')
        Aadhar1 =  request.FILES.get('Aadhar')
        Profile1 =  request.FILES.get('Profile')

        try:
            customer = UserProfile.objects.get(Mobile=Mobile,Aadhar_Number=Aadhar_Number)
            customer.Aadhar = Aadhar1
            customer.Profile = Profile1
            customer.KYC_status = 'Pending'
            customer.save()
            messages.success(request, "User KYC has request send successfully! wait for KYC updation")
            return redirect('user_login')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Profile not yet registered')
            return redirect('UserRegister')
    return render(request, 'KYC_update.html')

def user_login(request):
    if 'user_id' in request.session:
        return redirect('user_dashboard')
    if request.method == 'POST':
        Mobile = request.POST.get('Mobile')
        Password = request.POST.get("Password")
        try:
            customer=UserProfile.objects.get(Mobile=Mobile,Password=Password)
            if customer.KYC_status == 'Verified' and customer.Status == 'Active':
                request.session['First_Name'] = customer.First_Name
                request.session['user_id'] = customer.id
                return redirect('user_dashboard') 
            else:
                messages.error(request, f"Your account status: {customer.Status}, KYC Status: {customer.KYC_status}. Please wait for approval.")
                return redirect('user_login')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid Mobile or Password.')
            return redirect('user_login')
    else:
        return render(request, 'user_login.html')

def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('user_login')

def user_dashboard(request):
    if 'user_id' in request.session:
        return render(request, 'user_dashboard.html')
    return redirect('user_login')


def generate_unique_account_number():
    while True:
        account_no = random.randint(10**14, (10**15) - 1)  # 15-digit number
        if not UserAccount.objects.filter(Account_Number=account_no).exists():
            return account_no

        
def request_account(request):
    if 'user_id' in request.session:
        if request.method == "POST":


            user_id = request.session['user_id']
            user_profile = UserProfile.objects.get(id=user_id)
            Account_Type = request.POST.get("Account_Type")

            account_no = generate_unique_account_number()             
            account = UserAccount.objects.create(
                userProfile = user_profile,
                Account_Number = account_no,
                Account_Type = Account_Type,
                Account_Status = 'Processing',
                Account_Balance = '1000',
            )
        return render(request, 'request_account.html')
    return redirect('user_login')

def view_account(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user_profile = UserProfile.objects.get(id=user_id)
        account = UserAccount.objects.filter(userProfile=user_profile)
        context={
            'account':account
        }
        return render(request, 'view_account.html',context)
    return redirect('user_login')