from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'index.html')

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