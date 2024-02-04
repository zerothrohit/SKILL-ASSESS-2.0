import os
import pdfplumber
import google.generativeai as palm
import ast
from dotenv import load_dotenv
load_dotenv()
palm.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def get_text_from_resume_file(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def skills_extraction(text, description):
    # Configure PALM with your API key

    # Prepare the prompt with the {text} variable.
    prompt = f'''*ONLY* Extract all soft skills along with hard skills related to Computer Science, Information Technology, and related fields mentioned in the following text.
            Use the following {text} as input,
            * DO NOT AUTO-GENERATE SKILLS WHICH ARE NOT PRESENT, show skills which are mentioned in {text} only *

            Job Description:
            {description}
            '''
    # Generate text using the PALM model.
    response = palm.generate_text(
        prompt=prompt,
        temperature=0.2
    )
    # Return the generated text (extracted skills)
    return response.result


def question_generator(description, skills):
    prompt = f'''You are an experienced technical interviewer who takes interviews to test whether the candidate is apt for the the job role.
             Interview a candidate for the following job description: {description}.
             The candidate has the following skill set: {skills}.
             Based upon the job description and the candidates skillset you need to generate 20 questions in total.
             The formation of the questions should feel like as if a human interviewer is asking the question. Add a interviewer's style and verbal Inflections. Include pauses and vocal fillers in the questions just like in a transcript
             The generated questions should follow an evaluation criteria.
             Create 5 evaluation criteria and ask 2 questions for each criteria.
             Include criterias that are technology specific only.
             Don'ts: 1. Do not include any criteria which is coding orientied as this is only a verbal interview.
                     2. Do not include any criteria to evaluate soft skills, interpersonal or people skills.
             your output should be of python dictionary format where key of the dictionary is the criteria and value contains the question in list format.
             make sure that there is no * character in your response.'''
    response = palm.generate_text(prompt= prompt)
    questions=response.result
    if questions==None:
        response=palm.generate_text(prompt=prompt)
    print("=====================================================================")
    print(questions)
    print("=====================================================================")
    start_idx = questions.find('{')
    end_idx = questions.find('}')
    
    if start_idx != -1 and end_idx != -1:
        questions= questions[start_idx:end_idx+1]
        # questions_dict = ast.literal_eval(questions)
    else:
        questions= questions
        # questions_dict = ast.literal_eval(questions)
   
    questions_dict = ast.literal_eval(questions)
    # global criteria
    criteria=list(questions_dict.keys())

    question_list= []

    for sublist in questions_dict.values():
        question_list.extend(sublist)

    # with open('criteria.txt', 'w') as file:
    # # Write the content of the variable into the file
    #     file.write(str(criteria))
    
    return question_list