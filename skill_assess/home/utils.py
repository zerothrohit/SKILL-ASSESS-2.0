import os
import pdfplumber
import google.generativeai as palm
import ast
from dotenv import load_dotenv
import cv2
import numpy as np
import os
from keras.models import load_model
# Load pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load pre-trained emotion recognition model
emotion_model = load_model('facialemotionmodel.h5')

# Define emotions
emotions = ['Angry', 'Disgust', 'Fear', 'Confidence', 'Sad', 'Surprise', 'Neutral']

load_dotenv()
palm.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def get_text_from_resume_file(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def skills_extraction(text, description):
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
    start_idx = questions.find('{')
    end_idx = questions.find('}')
    
    if start_idx != -1 and end_idx != -1:
        questions= questions[start_idx:end_idx+1]
    else:
        questions= questions
   
    questions_dict = ast.literal_eval(questions)
    criteria=list(questions_dict.keys())

    question_list= []

    for sublist in questions_dict.values():
        question_list.extend(sublist)
    return question_list, criteria

def question_generator_hr(description, skills):
    prompt = f'''You are an experienced HR professional conducting interviews to assess whether the candidate aligns with the job role and organizational culture.
                Interview a candidate for the following job description: {description}.
                The candidate possesses the following skill set: {skills}.
                Based on the job description and the candidate's skill set, you need to generate 10 questions in total.
                Questions must be generated on the following evaluation criterias, each category should have 2 questions:  Leadership Potential, Work Ethic and Professionalism, Teamwork and Collaboration, Motivation and Passion, Adaptability and Learning Orientation
                The formation of the questions should emulate a human HR interviewer's style, incorporating verbal inflections, pauses, and vocal fillers. Craft questions that flow naturally in a conversation. 

                Your output should be in Python dictionary format, where the key is the evaluation criteria, and the value contains the questions in list format. Ensure there is no '*' character in your response.

                '''
    response = palm.generate_text(prompt= prompt)
    questions=response.result
    if questions==None:
        response=palm.generate_text(prompt=prompt)
    start_idx = questions.find('{')
    end_idx = questions.find('}')
    
    if start_idx != -1 and end_idx != -1:
        questions= questions[start_idx:end_idx+1]
    else:
        questions= questions
   
    questions_dict = ast.literal_eval(questions)
    criteria=list(questions_dict.keys())

    question_list= []

    for sublist in questions_dict.values():
        question_list.extend(sublist)
    return question_list, criteria

def evaluation(description,criteria1,criteria2,criteria3,criteria4,criteria5,questions_list,final_answers):
    evaluation_prompt=f'''your job is to evaluate an entire interview for the below job description:
    {description}

    The question are based on these five evaluation criterias {criteria1}, {criteria2}, {criteria3}, {criteria4}, {criteria5}
    Here is the list of questions asked to the candidate:
    {questions_list}
    And the below list contains the answers given by the candidate with respect to the questions asked:
    {final_answers}

    Based upon the answers given by candidate rate the skills of the candidate out of 10 points for each criteria and provide personalised feedback for improvements in each criteria.
    The feedback should be genuine so that the candidate can excel in the next interview.
    Return the response as a dictionary data type of python where key is the evaluation criteria of string type and value contains the rating and feedback to improve in list format'''    
    response = palm.generate_text(prompt= evaluation_prompt)
    evaluation=response.result
    start_idx = evaluation.find('{')
    end_idx = evaluation.find('}')
    
    if start_idx != -1 and end_idx != -1:
        evaluation= evaluation[start_idx:end_idx+1]
    else:
        evaluation= evaluation
    evaluation_dict = ast.literal_eval(evaluation)

    return evaluation_dict


## VIDEO ANALYSIS
def detect_faces_and_emotions(frame, emotion_counts):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        face_roi = cv2.resize(face_roi, (48, 48))
        face_roi = np.expand_dims(np.expand_dims(face_roi, -1), 0)
        emotion_pred = emotion_model.predict(face_roi)
        emotion_label = emotions[np.argmax(emotion_pred)]

        # Update emotion counts
        emotion_counts[emotion_label] += 1

        # Draw rectangle and emotion text on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, emotion_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    return frame

def video_analysis():
    # Directory where the videos are stored
    video_dir = "media"

    # Check if the number of video files is exactly 10
    if len([filename for filename in os.listdir(video_dir) if filename.endswith(".webm")]) != 10:
        print("There must be exactly 10 video files in the 'media' folder.")
        return

    # Dictionary to store outputs
    video_outputs = {}

    # Iterate over video files in the directory
    for filename in os.listdir(video_dir):
        if filename.endswith(".webm"):
            video_path = os.path.join(video_dir, filename)
            
            # Open video capture
            cap = cv2.VideoCapture(video_path)

            total_frames = 0
            emotion_counts = {emotion: 0 for emotion in emotions}

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                total_frames += 1

                frame = detect_faces_and_emotions(frame, emotion_counts)

                cv2.imshow('Video Emotion Detection', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Release the capture
            cap.release()
            cv2.destroyAllWindows()

            # Calculate combined percentages
            combined_percentage_angry_fear = (emotion_counts['Angry'] + emotion_counts['Fear']) / total_frames * 100
            combined_percentage_sad_disgust = (emotion_counts['Sad'] + emotion_counts['Disgust']) / total_frames * 100

            # Store output in the dictionary
            video_outputs[filename] = {
                "Combined Angry_Fear": combined_percentage_angry_fear,
                "Combined Sad_Disgust": combined_percentage_sad_disgust,
                "Confidence": (emotion_counts['Confidence'] / total_frames) * 100,
                "Surprise": (emotion_counts['Surprise'] / total_frames) * 100,
                "Neutral": (emotion_counts['Neutral'] / total_frames) * 100
            }

    # Print the dictionary
    print(video_outputs)

    # Initialize a dictionary to store cumulative counts for each emotion
    cumulative_counts = {'Combined Angry_Fear': 0, 'Combined Sad_Disgust': 0, 'Confidence': 0, 'Surprise': 0, 'Neutral': 0}

    # Iterate over video outputs
    for video_output in video_outputs.values():
        # Accumulate counts for each emotion
        for emotion, count in video_output.items():
            if emotion == 'Combined Angry_Fear':
                cumulative_counts['Combined Angry_Fear'] += count
            elif emotion == 'Combined Sad_Disgust':
                cumulative_counts['Combined Sad_Disgust'] += count
            elif emotion in cumulative_counts:
                cumulative_counts[emotion] += count

    # Calculate total number of frames across all videos
    total_frames_all_videos = sum([total_frames for total_frames in cumulative_counts.values()])

    # Check if total_frames_all_videos is not zero
    if total_frames_all_videos != 0:
        # Calculate cumulative percentages for each emotion
        cumulative_percentages = {emotion: (count / total_frames_all_videos) * 100 for emotion, count in cumulative_counts.items()}

        # Print cumulative percentages
        for emotion, percentage in cumulative_percentages.items():
            print(f"Cumulative {emotion}: {percentage:.2f}%")
    else:
        print("No frames processed across all videos.")

