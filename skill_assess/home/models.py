from django.db import models

# Create your models here.
class Resume(models.Model):
    file_path = models.FileField(upload_to='skill_assess/static/resumes') 
    round_type = models.CharField(max_length=50)
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()

    def __str__(self):
        return f"Resume {self.id}: {self.job_title}"
