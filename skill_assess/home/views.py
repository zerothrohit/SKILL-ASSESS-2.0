from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from home.models import Resume
from django.core.files.storage import default_storage
from django.http import HttpResponse
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.auth.decorators import login_required
from .utils import get_text_from_resume_file, skills_extraction, question_generator, evaluation, question_generator_hr
from .decorators import custom_login_required
import os
from django.urls import reverse

from django.contrib.auth import logout

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

import json,time

# Create your views here.

job_description=""

criterias=[]

questions=[]

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
        global job_description
        job_description = last_resume.job_description

        # Fetch the resume file from S3 and extract text (you may need to implement this)
        # For demonstration purposes, let's assume there's a function get_text_from_resume_file
        resume_text = get_text_from_resume_file(resume_file_path)


        skills=skills_extraction(resume_text,job_description)
        if round_type == 'technical':
            questions_and_criterias = question_generator(job_description, skills)
        elif round_type == 'hr':
            questions_and_criterias = question_generator_hr(job_description, skills)
        global criterias
        global questions
        questions, criterias = questions_and_criterias[0],questions_and_criterias[1]


        # Transform questions to the desired structure
        transformed_questions = [{"title": f"Question {i+1}", "text": question} for i, question in enumerate(questions)]
        # Render the stream page with resume details and transformed questions
        return render(request, 'stream.html', {'questions': transformed_questions})

    else:
        # Handle the case where there is no resume uploaded
        return HttpResponse('error')







user_answers = {}  # Define outside the function to persist between requests




@csrf_exempt

def save_answer(request):

    global user_answers




    if request.method == 'POST':

        data = json.loads(request.body)

        question = data.get('question')

        time.sleep(12)

        answer = data.get('answer')




        # Save the answer to the user_answers dictionary

        user_answers[question] = answer




        # Check if all questions have been answered

        if len(user_answers) == 10:  # Assuming you have 10 questions

            print("All questions answered:")

            print("===========================================")

            print(user_answers)

            print("===========================================")

            return redirect('feedback')

            # global job_description, criterias, questions

            # feedback_dict = evaluation(job_description, criterias[0], criterias[1], criterias[2], criterias[3], criterias[4], questions, user_answers)

            # return render(request, 'feedback.html', {'feedback_dict': feedback_dict})







        # If not all questions are answered, return a JsonResponse indicating success

        return JsonResponse({'message': 'Answer saved successfully.'})




    else:

        return JsonResponse({'error': 'Invalid request method.'}, status=405)




@csrf_exempt
def save_video(request):
    if request.method == 'POST':
        data = request.FILES['video']
        question_number = request.POST.get('question_number')

        # Define the directory where you want to save the videos
        save_dir = 'skill_assess/media/'

        # Ensure the directory exists, create it if not
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save the video file
        video_path = os.path.join(save_dir, f'video_{question_number}.webm')
        with open(video_path, 'wb') as f:
            for chunk in data.chunks():
                f.write(chunk)

        return redirect('feedback')

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
    

def feedback(request):

    global job_description, criterias, questions, user_answers

    feedback_dict = evaluation(job_description, criterias[0], criterias[1], criterias[2], criterias[3], criterias[4], questions, user_answers)

    print(feedback_dict)

    return render(request, 'feedback.html', {'feedback_dict': feedback_dict})

