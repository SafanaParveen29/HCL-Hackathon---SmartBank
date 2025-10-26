from django.test import TestCase, Client
from django.urls import reverse
from . models import UserProfile, UserAccount
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

class SmartBankTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create(
            First_Name="John",
            Last_Name="Doe",
            Mobile="9999999999",
            Email="john@example.com",
            Aadhar_Number="123412341234",
            DOB="2000-01-01",
            Address="123 Street, City",
            Password="pass123",
            KYC_status="Verified",
            Status="Active",
        )

    def test_user_register_valid(self):
        """✅ Test successful user registration"""
        response = self.client.post(reverse('UserRegister'), {
            'First_Name': 'Jane',
            'Last_Name': 'Smith',
            'Mobile': '8888888888',
            'Email': 'jane@example.com',
            'Aadhar_Number': '123456789012',
            'DOB': '1995-01-01',
            'Address': '456 Street',
            'Password': 'pass123',
            'Confirm_Password': 'pass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('KYC_update'))
        self.assertTrue(UserProfile.objects.filter(Mobile='8888888888').exists())

    def test_user_register_invalid_mobile(self):
        """🚫 Invalid mobile number check"""
        response = self.client.post(reverse('UserRegister'), {
            'First_Name': 'Jane',
            'Last_Name': 'Smith',
            'Mobile': '12345',  # invalid
            'Email': 'jane@example.com',
            'Aadhar_Number': '123456789012',
            'DOB': '1995-01-01',
            'Address': '456 Street',
            'Password': 'pass123',
            'Confirm_Password': 'pass123',
        })
        self.assertRedirects(response, reverse('UserRegister'))
        self.assertFalse(UserProfile.objects.filter(Email='jane@example.com').exists())

    def test_user_login_valid(self):
        """✅ Valid user login"""
        response = self.client.post(reverse('user_login'), {
            'Mobile': '9999999999',
            'Password': 'pass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_dashboard'))
        self.assertIn('user_id', self.client.session)

    def test_user_login_invalid(self):
        """🚫 Invalid login credentials"""
        response = self.client.post(reverse('user_login'), {
            'Mobile': '9999999999',
            'Password': 'wrongpass'
        })
        self.assertRedirects(response, reverse('user_login'))
        self.assertNotIn('user_id', self.client.session)

    def test_request_account(self):
        """✅ Account request with initial balance"""
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        response = self.client.post(reverse('request_account'), {
            'Account_Type': 'Savings',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserAccount.objects.filter(userProfile=self.user).exists())
        account = UserAccount.objects.get(userProfile=self.user)
        self.assertEqual(account.Account_Balance, '1000')

    def test_view_account(self):
        """✅ View account details"""
        account = UserAccount.objects.create(
            userProfile=self.user,
            Account_Number="123456789012345",
            Account_Type="Savings",
            Account_Status="Active",
            Account_Balance="2000"
        )
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        response = self.client.get(reverse('view_account'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, account.Account_Number)

    def test_kyc_update(self):
        """✅ Upload KYC files"""
        aadhar_file = SimpleUploadedFile("aadhar.jpg", b"file_content", content_type="image/jpeg")
        profile_file = SimpleUploadedFile("profile.jpg", b"file_content", content_type="image/jpeg")

        response = self.client.post(reverse('KYC_update'), {
            'Mobile': '9999999999',
            'Aadhar_Number': '123412341234',
            'Aadhar': aadhar_file,
            'Profile': profile_file,
        })
        self.assertRedirects(response, reverse('user_login'))
        updated_user = UserProfile.objects.get(Mobile='9999999999')
        self.assertEqual(updated_user.KYC_status, 'Pending')
