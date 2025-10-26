🏦 SmartBank System (Django)

A secure and user-friendly online banking system built with \*\*Django\*\*, allowing users to register, 

complete KYC verification, log in, and request bank accounts (Savings, Current, or FD).  

Admins can later approve or manage users and accounts.


🚀 Features



\- 👤 \*\*User Registration\*\* with validation (mobile, email)

\- 🪪 \*\*KYC Update\*\* with file upload for Aadhar and profile photo

\- 🔐 \*\*User Login/Logout\*\*

\- 💰 \*\*Account Request\*\* — automatically generates a 15-digit account number and initializes with ₹1000

\- 🧾 \*\*View Account\*\* — view all accounts created by a user

\- 🧠 \*\*Session Management\*\* — user sessions maintained securely

\- ✅ \*\*Unit Testing\*\* for views, login, registration, and account features


---

\## 🧰 Tech Stack



| Component | Technology |

|------------|-------------|

| \*\*Backend\*\* | Django 4.2.7 / Python 3.11.4 |

| \*\*Database\*\* | SQLite (default) |

| \*\*Frontend\*\* | HTML, CSS (Django Templates) |

| \*\*Testing\*\* | Django Test Framework |

| \*\*File Uploads\*\* | Django `FileField` (Aadhar, Profile) |



---



Install Dependencies

pip install -r requirements.txt


URLS:

&nbsp;  path('User-Register/',views.UserRegister, name='UserRegister'),    

&nbsp;   path('KYC-Update/',views.KYC\_update, name='KYC\_update'),    

&nbsp;   path('User-login/',views.user\_login, name='user\_login'),    

&nbsp;   path('user\_logout/',views.user\_logout, name='user\_logout'),    

&nbsp;   path('',views.user\_dashboard, name='user\_dashboard'),    

&nbsp;   path('Request-Account',views.request\_account, name='request\_account'),

&nbsp;   path('View-Account',views.view\_account, name='view\_account'),

**UNIT TEST - Result**

D:\HCL\SmartBank>python manage.py test myapp
Found 0 test(s).
System check identified some issues:

WARNINGS:
?: (staticfiles.W004) The directory 'D:\HCL\SmartBank\static' in the STATICFILES_DIRS setting does not exist.

System check identified 1 issue (0 silenced).

----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK


SmartBank — User Registration \& KYC (README / System Design) - Account Creation

**Goals**

•	Fast, secure onboarding: collect personal data + documents for KYC

•	Parallel handling: Verify KYC by admin and accept profile with

•	Verify KYC using Aadhar Number and Aadhar Card

•	Auditable, compliant storage \& logging; encryption at rest/in transit.



Components \& responsibilities:

•	Client : Register – Verify KYC – Login – Create Account

•	Admin : Verify and Approved KYC, Update Registration Status



Sequence flow (step-by-step):

•	Client submits profile + files to - /registrations

•	Gateway performs basic validation \& authenticity checks.

•	API save user row (PENDING\_KYC) and save files to S3 with temporary access policy (do not expose publicly).

•	API publishes message to queue and returns 201



Workflow Overview:



User Registration (Frontend → Django API)

•	User fills in personal details (email, name, DOB, phone) and uploads KYC documents (ID proof, selfie, etc.).

•	Frontend sends a multipart/form-data POST request to /api/v1/registrations/.

•	Django REST API validates inputs and:

•	Creates a new User in auth\_user table.

•	Creates a linked UserProfile with status PENDING.

•	Uploads documents to S3 via django-storages.

•	Saves metadata in KYCDocument table.

•	Django immediately queues a Celery task process\_kyc\_for\_profile.delay(profile\_id).

•	Response: { "registration\_id": "uid", "status": "PENDING" } returned to user.



Background KYC Processing (Celery Worker)

•	The Celery worker fetches the UserProfile and associated documents.

•	For each document:

•	Runs virus scan (e.g., ClamAV).

•	Extracts text with OCR (e.g., Tesseract or AWS Textract).

•	If selfie provided, runs face-match check between ID and selfie.

•	Sends data to external KYC/AML provider for verification.

•	Saves results to validation\_result JSON.



Decision Logic:

•	If all checks pass → kyc\_status = VERIFIED

•	If some low confidence results → MANUAL\_REVIEW

•	If mismatch or invalid → REJECTED

•	Updates the profile and document records.

•	Creates a new entry in KYCEvent table (e.g., KYC\_COMPLETED).



Notification \& Manual Review (Optional)

•	Once status changes, the user can poll /api/v1/registrations/{id}/ to check the KYC status.

•	Admin UI displays all PENDING or MANUAL\_REVIEW profiles.

•	Admin can approve, reject, or resubmit KYC manually.



Data Storage

•	User Data → PostgreSQL (encrypted fields)

•	KYC Documents → S3 (AES256 encryption, versioned)

•	Audit Events → PostgreSQL KYCEvent table

•	Security Controls

•	HTTPS + JWT authentication.

•	File validation (type/size).

•	Encrypted S3 storage.

•	Celery retry with exponential backoff.

•	Role-based admin permissions.



Sequence Diagram (text)

•	User → Django API: POST /api/v1/registrations

•	Django API → DB: Save user + profile + documents

•	Django API → Celery: enqueue process\_kyc\_for\_profile(profile\_id)

•	Celery → S3: read documents

•	Celery → OCR/Face/3rd-party: validate identity

•	Celery → DB: update status = VERIFIED

•	Celery → Audit: log event 'KYC\_COMPLETED'

•	User ← Django API: GET /registrations/{id} → status VERIFIED





Worker consumes message:

•	Virus scan

•	OCR → extract fields

•	Face detect \& compare selfie to ID photo (or call liveness)

•	Business rules \& third-party calls

•	admin updates kyc\_documents and users.kYC\_status (VERIFIED / REJECTED / MANUAL\_REVIEW).

•	If MANUAL\_REVIEW, case created in Admin UI with all artifacts.



Validation \& business rules (examples)

•	Name match tolerance: Levenshtein distance <= 2 for common typos.

•	DOB exact match or within acceptable variance when OCR quality low — flags for manual review.

•	ID expiry check: reject if expired.

•	Document formats allowed: PDF, JPG, PNG; max size 10MB/file.

•	Max attempts per user: e.g., 3 attempts before escalation.

•	Geo/locale rules: different required docs by country.

•	Error handling \& manual review

•	Clear error codes for client (e.g., 400 validation, 202 accepted w/ processing, 409 duplicate).

•	Store detailed failure reason in kyc\_documents.validation\_result.

•	Manual review UI shows OCR text, images, comparison score, recent events, ability to override and annotate.

Unit Tests

•	We'll write tests for:

•	User registration API endpoint (multipart request).

•	Document upload validation.

•	Celery KYC processing task.

•	Audit event creation.



Test tools:

•	pytest or Django’s unittest style.

•	rest\_framework.test.APIClient for API calls.

•	unittest.mock for mocking Celery tasks \& file storage.





Deployment Flow

•	Deploy Django + Celery using Docker.

•	Apply migrations.

•	Start workers: celery -A smartbank worker -l info.

•	Run tests: pytest -v.

•	Monitor using Flower or Grafana.













SmartBank — User Registration \& KYC (README / System Design) - Account Creation

Goals

•	Fast, secure onboarding: collect personal data + documents for KYC

•	Parallel handling: Verify KYC by admin and accept profile with

•	Verify KYC using Aadhar Number and Aadhar Card

•	Auditable, compliant storage \& logging; encryption at rest/in transit.



Components \& responsibilities:

•	Client : Register – Verify KYC – Login – Create Account

•	Admin : Verify and Approved KYC, Update Registration Status



Sequence flow (step-by-step):

•	Client submits profile + files to - /registrations

•	Gateway performs basic validation \& authenticity checks.

•	API save user row (PENDING\_KYC) and save files to S3 with temporary access policy (do not expose publicly).

•	API publishes message to queue and returns 201



Workflow Overview:



User Registration (Frontend → Django API)

•	User fills in personal details (email, name, DOB, phone) and uploads KYC documents (ID proof, selfie, etc.).

•	Frontend sends a multipart/form-data POST request to /api/v1/registrations/.

•	Django REST API validates inputs and:

•	Creates a new User in auth\_user table.

•	Creates a linked UserProfile with status PENDING.

•	Uploads documents to S3 via django-storages.

•	Saves metadata in KYCDocument table.

•	Django immediately queues a Celery task process\_kyc\_for\_profile.delay(profile\_id).

•	Response: { "registration\_id": "uid", "status": "PENDING" } returned to user.



Background KYC Processing (Celery Worker)

•	The Celery worker fetches the UserProfile and associated documents.

•	For each document:

•	Runs virus scan (e.g., ClamAV).

•	Extracts text with OCR (e.g., Tesseract or AWS Textract).

•	If selfie provided, runs face-match check between ID and selfie.

•	Sends data to external KYC/AML provider for verification.

•	Saves results to validation\_result JSON.



Decision Logic:

•	If all checks pass → kyc\_status = VERIFIED

•	If some low confidence results → MANUAL\_REVIEW

•	If mismatch or invalid → REJECTED

•	Updates the profile and document records.

•	Creates a new entry in KYCEvent table (e.g., KYC\_COMPLETED).



Notification \& Manual Review (Optional)

•	Once status changes, the user can poll /api/v1/registrations/{id}/ to check the KYC status.

•	Admin UI displays all PENDING or MANUAL\_REVIEW profiles.

•	Admin can approve, reject, or resubmit KYC manually.



Data Storage

•	User Data → PostgreSQL (encrypted fields)

•	KYC Documents → S3 (AES256 encryption, versioned)

•	Audit Events → PostgreSQL KYCEvent table

•	Security Controls

•	HTTPS + JWT authentication.

•	File validation (type/size).

•	Encrypted S3 storage.

•	Celery retry with exponential backoff.

•	Role-based admin permissions.



Sequence Diagram (text)

•	User → Django API: POST /api/v1/registrations

•	Django API → DB: Save user + profile + documents

•	Django API → Celery: enqueue process\_kyc\_for\_profile(profile\_id)

•	Celery → S3: read documents

•	Celery → OCR/Face/3rd-party: validate identity

•	Celery → DB: update status = VERIFIED

•	Celery → Audit: log event 'KYC\_COMPLETED'

•	User ← Django API: GET /registrations/{id} → status VERIFIED





Worker consumes message:

•	Virus scan

•	OCR → extract fields

•	Face detect \& compare selfie to ID photo (or call liveness)

•	Business rules \& third-party calls

•	admin updates kyc\_documents and users.kYC\_status (VERIFIED / REJECTED / MANUAL\_REVIEW).

•	If MANUAL\_REVIEW, case created in Admin UI with all artifacts.



Validation \& business rules (examples)

•	Name match tolerance: Levenshtein distance <= 2 for common typos.

•	DOB exact match or within acceptable variance when OCR quality low — flags for manual review.

•	ID expiry check: reject if expired.

•	Document formats allowed: PDF, JPG, PNG; max size 10MB/file.

•	Max attempts per user: e.g., 3 attempts before escalation.

•	Geo/locale rules: different required docs by country.

•	Error handling \& manual review

•	Clear error codes for client (e.g., 400 validation, 202 accepted w/ processing, 409 duplicate).

•	Store detailed failure reason in kyc\_documents.validation\_result.

•	Manual review UI shows OCR text, images, comparison score, recent events, ability to override and annotate.

Unit Tests

•	We'll write tests for:

•	User registration API endpoint (multipart request).

•	Document upload validation.

•	Celery KYC processing task.

•	Audit event creation.



Test tools:

•	pytest or Django’s unittest style.

•	rest\_framework.test.APIClient for API calls.

•	unittest.mock for mocking Celery tasks \& file storage.





Deployment Flow

•	Deploy Django + Celery using Docker.

•	Apply migrations.

•	Start workers: celery -A smartbank worker -l info.

•	Run tests: pytest -v.

•	Monitor using Flower or Grafana.













"# HCL-Hackathon---SmartBank" 
