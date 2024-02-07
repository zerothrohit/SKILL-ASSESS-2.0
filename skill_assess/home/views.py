from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from home.models import Resume
from django.core.files.storage import default_storage
from django.http import HttpResponse
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.auth.decorators import login_required
from .decorators import custom_login_required
from django.urls import reverse
from django.contrib.auth import logout
from .utils import get_text_from_resume_file, skills_extraction, question_generator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to resume_upload page after successful login
            return redirect(reverse('resume_upload') + f'?username={username}')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, "login.html", {'error_message': "Invalid username or password."})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('index')

def about(request):
    return render(request,'about.html')


class MediaStorage(S3Boto3Storage):
    location = 'resume/'
    file_overwrite = False

    

@custom_login_required
def resume_upload(request):
    if request.method == 'POST':
        pdf_file = request.FILES['resume_file']
        # Save the file to S3 using the custom storage class
        file_path = default_storage.save(f'resume/{pdf_file.name}', pdf_file)

#         # You can get the URL of the saved file using the custom storage class
        file_url = default_storage.url(file_path)
        round_type = request.POST.get('round')
        job_title = request.POST.get('job-title')
        job_description = request.POST.get('job-description')
        base_url = file_url.split('?')[0]
        # Associate the resume with the currently logged-in user
        resume_object = Resume(
            user=request.user,
            file_path=f'resume/{pdf_file.name}',
            round_type=round_type,
            job_title=job_title,
            job_description=job_description
        )
        resume_object.save()
        print("File URL:", base_url)
        return redirect('stream')

    return render(request, 'resume.html')

@custom_login_required
def stream(request):
    # Fetch the last uploaded resume details of the current user
    last_resume = Resume.objects.filter(user=request.user).last()

    if last_resume:
        # Extract information from the last uploaded resume
        resume_file_path = last_resume.file_path
        round_type = last_resume.round_type
        job_title = last_resume.job_title
        job_description = last_resume.job_description

        # Fetch the resume file from S3 and extract text (you may need to implement this)
        # For demonstration purposes, let's assume there's a function get_text_from_resume_file
        resume_text = get_text_from_resume_file(resume_file_path)

        # Print details in the terminal (replace print statements with your desired actions)
        print("Resume Text:", resume_text)
        print("Round Type:", round_type)
        print("Job Title:", job_title)
        print("Job Description:", job_description)

        skills=skills_extraction(resume_text,job_description)
        questions = question_generator(job_description, skills)
        print(questions)
        
        # Transform questions to the desired structure
        transformed_questions = [{"title": f"Question {i+1}", "text": question} for i, question in enumerate(questions)]
        print(transformed_questions)

        # Render the stream page with resume details and transformed questions
        return render(request, 'stream.html', {'questions': transformed_questions})
    
    else:
        # Handle the case where there is no resume uploaded
        return HttpResponse('error')




user_answers = {}  # Define outside the function to persist between requests

@csrf_exempt
def save_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        answer = data.get('answer')
        
        # Save the answer to the user_answers dictionary
        user_answers[question] = answer

        # Check if all questions have been answered
        if len(user_answers) == 10:  # Assuming you have 10 questions
            print("All questions answered:")
            for question, answer in user_answers.items():
                print(f"Question: {question}, Answer: {answer}")

        return JsonResponse({'message': 'Answer saved successfully.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


