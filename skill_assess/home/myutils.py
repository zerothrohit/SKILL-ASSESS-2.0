import os
import google.generativeai as palm
import ast
from dotenv import load_dotenv
import cv2
import numpy as np
import os
from keras.models import load_model
load_dotenv()
palm.configure(api_key=os.getenv('GOOGLE_API_KEY'))
description = '''Job Description:

Must-Have Skills:

•Python: Extensive expertise in Python for data analysis, scripting, and automation.
•Excel & PowerPoint: Advanced skills in Excel for data analysis and in PowerPoint for presenting findings.
•SQL: Proficient in SQL for data querying, extraction, and database management.
•Machine Learning (Supervised & Unsupervised): Proven experience in applying both supervised and unsupervised machine learning techniques.
•Forecasting Techniques: Strong understanding and application of advanced forecasting techniques.
•Hands-on experience in implementing optimization models using Machine Learning Programming (MLP) and Linear Regression



Good-to-Have Skills:

•Azure Data Factory: Familiarity with Azure Data Factory for ETL (Extract, Transform, Load) processes.
•Azure Data Bricks: Knowledge of Azure Data Bricks for big data analytics and machine learning.
•Data Modeling: Understanding of data modeling concepts to ensure effective database design.


Responsibilities:

•Data Analysis: Utilize Python, Excel, and SQL to perform in-depth analysis of large and complex datasets.
•Machine Learning: Apply advanced supervised and unsupervised machine learning techniques to develop predictive models.
•Forecasting Techniques: Employ sophisticated forecasting techniques to predict trends and outcomes.
•Machine Learning Programming (MLP) and Linear Regression to enhance decision-making processes.
•Reporting and Visualization: Develop insightful dashboards and reports using Excel and PowerPoint for effective communication of findings.'''

criteria1 = "Machine learning Knowledge"
criteria2 = "Time series understanding"
criteria3 = "Excel Skills"
criteria4 = "Python skills"
criteria5 = "SQL Skills"

questions_list = '''['Can you tell me about your experience with Python?', 'What are some of the things you like about Python?', 'What are your skills in Excel and PowerPoint?', "Can you give me an example of a dashboard you've created in Excel?", 'What are your skills in SQL?', "Can you give me an example of a query you've written?", 'What are your skills in machine learning?', "Can you give me an example of a machine learning model you've built?", 'What are your skills in forecasting techniques?', "Can you give me an example of a forecasting model you've built?"]'''
final_answers = '''{'Question 1': 'I have used 510 and multiple data science projects.', 'Question 2': "By then it's very easy to understand and implement and you can do various things by importing just the library.", 'Question 3': "I've used Microsoft Excel for overbilling dashboards and PowerPoint for building presentations.", 'Question 4': 'i would have loved to dashboard for amazon things would have included the important kpis and', 'Question 5': 'I know multiple DML commands and clauses like wildflowers having class and I can create a well organized schema also.', 'Question 6': 'I literally just like complex SELECT queries in SQL and have also indicated SQL in my Python app.', 'Question 7': 'I know many different types of algorithms, including supervised, unsupervised and supervised.', 'Question 8': "I've built multiple models but few of them are LSTM which I've used for sequential data or data.", 'Question 9': 'I know various models in time series analysis like ARIMA, SARIMA.', 'Question 10': 'i have been and forecasting model in my internship to flag'}'''


def evaluation(description, criteria1, criteria2, criteria3, criteria4, criteria5, questions_list, final_answers):
    evaluation_prompt = f'''You are an 10 year old strict and experience technical interviewer you have worked in various companies in past and hired over 700+ brilliant talents and skilled people.Your job is to evaluate an entire interview for the below job description:
    {description}

    The question are based on these five evaluation criterias {criteria1}, {criteria2}, {criteria3}, {criteria4}, {criteria5}
    Here is the list of questions asked to the candidate:
    {questions_list}
    And the below list contains the answers given by the candidate with respect to the questions asked:
    {final_answers}

    Based upon the answers given by candidate score the skills of the candidate out of 0 to 10 points for each criteria make sure your score is genuine, give a poor score (0-4 score ) if the answers are not descriptive enough, not explained in depth and a good score (5-10 score ) if the candidate seems to be a good fit for the job and provide personalised feedback for improvements in each criteria. You need to analyse whether the answers are fundamentally correct and properly described by the candidate.
    The feedback should be genuine so that the candidate can excel in the next interview.
    Return the response as a dictionary data type of python where key is the evaluation criteria of string type and value contains the rating and feedback to improve in list format 
    The feedback should be genuine so that the candidate can excel in the next interview.

    Return the response as a dictionary data type of Python where the key is the evaluation criteria of string type and the value contains the rating and feedback to improve in a list format.


Give a score of 0-4 only if:

The answer partially addresses the question but lacks coherence or relevance, or is somewhat off-topic.
The response provides some description but lacks depth or adequate explanation, leaving some gaps in understanding.
The answer is somewhat brief, providing some detail but lacking in sufficient depth to fully convey the information.
The response contains some meaningful content but also includes irrelevant or tangential information that detracts from the overall relevance.
The answer includes some essential details but lacks consistency or thoroughness in addressing all aspects of the topic.
The candidate attempts to answer the question but provides an incomplete or unclear response, or explicitly indicates difficulty in responding.

These conditions set clear and solid criteria for assigning lower scores, ensuring that candidates receive poor ratings when their answers do not meet the expected standards for depth, relevance, and clarity.

Give a score of 5-10 only if:
1. The answer is meaningful and directly addresses the question.
2. The answer demonstrates depth, quality, and genuineness.
3. If answer is elaborate

Give a score of 8-10 only if:

The answer directly addresses the question comprehensively, covering all aspects.
The response demonstrates exceptional depth, quality, and genuineness.
The answer is not only elaborate but also provides insightful perspectives or additional relevant information beyond what is expected.
The candidate's communication is clear, concise, and well-structured.
The response showcases a profound understanding of the subject matter, potentially offering innovative solutions or approaches.
The candidate effectively incorporates relevant examples or experiences to support their answer.
Overall, the answer significantly exceeds expectations and indicates the candidate's exceptional suitability for the job.
Please ensure that the scores and feedback provided are sincere and constructive, aiming to help the candidate improve their performance in future interviews. The feedback should be descriptive so that the candidate can work on his weaknesses.'''

    response = palm.generate_text(prompt=evaluation_prompt)
    evaluation = response.result
    start_idx = evaluation.find('{')
    end_idx = evaluation.find('}')

    if start_idx != -1 and end_idx != -1:
        evaluation = evaluation[start_idx:end_idx+1]
    else:
        evaluation = evaluation
    evaluation_dict = ast.literal_eval(evaluation)
    print(evaluation_dict)
    return evaluation_dict


evaluation(description, criteria1, criteria2, criteria3,
           criteria4, criteria5, questions_list, final_answers)
