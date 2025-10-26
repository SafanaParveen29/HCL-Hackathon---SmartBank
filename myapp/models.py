from django.db import models

class UserProfile(models.Model):
    STATUS_CHOICES = [
    ('Not_Updated','Not Updated'),
    ('Pending', 'Pending'),
    ('Verified', 'Verified'),
    ('Rejected', 'Rejected'),
    ('Review', 'Review'),
    ]

    STATUS_CHOICES1 = [
    ('Pending', 'Pending'),
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
    ('Processing', 'Processing'),
    ]

    First_Name = models.CharField(max_length=50)
    Last_Name = models.CharField(max_length=50)
    Mobile = models.CharField(max_length=10,unique=True)
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=50,null=True, blank=True)
    Aadhar_Number = models.CharField(max_length=12)
    DOB = models.DateField(null=True, blank=True)
    Address = models.TextField()    
    KYC_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not_Updated')
    Aadhar = models.FileField(upload_to='Aadhar/',null=True, blank=True)
    Profile = models.FileField(upload_to='profile/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    Status = models.CharField(max_length=20, choices=STATUS_CHOICES1, default='Pending')

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name} - KYC Status: {self.KYC_status} -  Account Status: {self.    Status}  "

class UserAccount(models.Model):
    STATUS_CHOICES = [
    ('Savings','Savings'),
    ('Current', 'Current'),
    ('FD', 'FD'),
    ]

    STATUS_CHOICES1 = [
    ('Pending', 'Pending'),
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
    ('Processing', 'Processing'),
    ]

    userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    Account_Number = models.CharField(max_length=16,unique=True)
    Account_Type = models.CharField(max_length=20, choices=STATUS_CHOICES, default=' ')
    Account_Status = models.CharField(max_length=20, choices=STATUS_CHOICES1, default='Pending')
    Account_Balance = models.CharField(max_length=20,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.userProfile.First_Name} - {self.Account_Number} "



