from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from home.models import Resume
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pdfplumber
# Create your views here.
def index(request):
    return render(request,'index.html')

def register(request):
    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        confirmPassword=request.POST['confirmPassword']

        myuser=User.objects.create_user(username,email,password)
        myuser.save()
        messages.success(request,"Your skillassess account has been successfully created.")
        return redirect('login')
    
    return render(request,'register.html')

def Login(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(username=username,password=password)

        if user is not None:
            login(request,user)
            return render(request,"about.html",{'username':username})
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, "login.html", {'error_message': "Invalid username or password."})

    return render(request, "login.html")
def about(request):
    return render(request,'about.html')

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text_content = ""
        for page in pdf.pages:
            text_content += page.extract_text()
    return text_content


from django.http import HttpResponseBadRequest

# def resume_upload(request):
#     if request.method == 'POST':
#         print(request.FILES)
#         if 'resume' in request.FILES:
#             resume_file = request.FILES['resume']
#             round_type = request.POST.get('round')
#             job_title = request.POST.get('job-title')
#             job_description = request.POST.get('job-description')

#             file_path = f'resume/{resume_file.name}'
#             default_storage.save(file_path, resume_file)

#             new_resume = Resume(
#                 file_path=file_path,
#                 round_type=round_type,
#                 job_title=job_title,
#                 job_description=job_description
#             )
#             new_resume.save()

#             return HttpResponse('Resume submitted successfully!')
#         else:
#             return HttpResponseBadRequest('No file selected. Please choose a file.')

#     return render(request, 'resume.html')


from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'resume/'
    file_overwrite = False

# def resume_upload(request):
#     if request.method == 'POST':


#         pdf_file = request.FILES['resume_file']

#         # Save the file to S3 using the custom storage class
#         file_path = default_storage.save(f'resume/{pdf_file.name}', pdf_file)

#         # You can get the URL of the saved file using the custom storage class
#         file_url = default_storage.url(file_path)

#         round_type = request.POST.get('round')
#         job_title = request.POST.get('job-title')
#         job_description = request.POST.get('job-description')

#         return HttpResponse('Resume submitted successfully!')  # Redirect to a success page

#     return render(request, 'resume.html')


from django.shortcuts import render, HttpResponse
from .models import Resume

def resume_upload(request):
    if request.method == 'POST':
        pdf_file = request.FILES['resume_file']

        # Save the file to S3 using the custom storage class
        file_path = default_storage.save(f'resume/{pdf_file.name}', pdf_file)

        # You can get the URL of the saved file using the custom storage class
        file_url = default_storage.url(file_path)

        round_type = request.POST.get('round')
        job_title = request.POST.get('job-title')
        job_description = request.POST.get('job-description')
    
        base_url = file_url.split('?')[0]
        

        # Create a Resume object and save it to the database
        resume_object = Resume(
            file_path=base_url,
            round_type=round_type,
            job_title=job_title,
            job_description=job_description
        )
        resume_object.save()
        print("File URL:", base_url)

        return HttpResponse('Resume submitted successfully!')  # Redirect to a success page

    return render(request, 'resume.html')

