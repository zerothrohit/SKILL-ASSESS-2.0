from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
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

def resume_upload(request):
    if request.method=="POST":
        # resume=request.POST['resume']
        round=request.POST['round']
        job_title=request.POST['job-title']
        job_description=request.POST['job-description']
        print(round,job_title,job_description)
    return render(request,'resume.html')