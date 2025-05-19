from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
import os
from django.conf import settings
from django.core.files.storage import default_storage
from PyPDF2 import PdfReader
import docx
import random
from django.http import JsonResponse
import google.generativeai as genai
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from interview_platform.emotion_detector import detect_emotion_from_frame
import base64
import numpy as np
import cv2

def index(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Here you would typically validate the credentials
        # For now, we'll just redirect to dashboard
        return redirect('dashboard')
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'signup.html')
        
        # Store user information in session
        request.session['user_fullname'] = fullname
        request.session['user_email'] = email

        # Here you would typically create a new user and log them in
        # For now, we'll just redirect to login (which then redirects to dashboard)
        messages.success(request, 'Signup successful! Please log in.')
        return redirect('index')
    return render(request, 'signup.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def interview(request):
    if request.method == 'POST':
        # Get form data
        job_role = request.POST.get('jobRole')
        experience = request.POST.get('experience')
        interview_type = request.POST.get('interviewType')
        duration = request.POST.get('duration')
        focus_areas = request.POST.getlist('focus')
        
        # Here you would typically start the interview process
        # For now, we'll just redirect to the interview page
        return redirect('interview')
    return render(request, 'interview.html')

def start_interview(request):
    # Get questions from session
    questions = request.session.get('interview_questions', [])
    return render(request, 'start-interview.html', {'questions': questions})

def extract_skills_from_text(text):
    # Simple predefined list of skills
    skills_list = [
        'python', 'java', 'c++', 'javascript', 'sql', 'html', 'css', 'django', 'flask', 'react', 'node',
        'machine learning', 'data analysis', 'excel', 'git', 'linux', 'aws', 'docker', 'kubernetes',
        'communication', 'leadership', 'project management', 'problem solving', 'teamwork', 'agile',
    ]
    found_skills = set()
    text_lower = text.lower()
    for skill in skills_list:
        if skill in text_lower:
            found_skills.add(skill.title())
    return sorted(found_skills)

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def generate_questions_for_skills(skills):
    # Dictionary of questions for each skill
    skill_questions = {
        'Python': [
            'Explain the difference between lists and tuples in Python.',
            'What are decorators in Python?',
            'How does Python handle memory management?',
            'Explain the concept of generators in Python.',
            'What is the difference between deep copy and shallow copy?'
        ],
        'Java': [
            'Explain the concept of inheritance in Java.',
            'What is the difference between abstract class and interface?',
            'How does garbage collection work in Java?',
            'Explain the concept of multithreading in Java.',
            'What are the different types of exceptions in Java?'
        ],
        'C++': [
            'What is the difference between stack and heap memory?',
            'Explain the concept of virtual functions.',
            'What are smart pointers in C++?',
            'How does multiple inheritance work in C++?',
            'Explain the concept of templates.'
        ],
        'Javascript': [
            'Explain the concept of closures in JavaScript.',
            'What is the difference between let, const, and var?',
            'How does event bubbling work?',
            'Explain the concept of promises.',
            'What is the difference between == and ===?'
        ],
        'SQL': [
            'What is the difference between INNER JOIN and LEFT JOIN?',
            'Explain the concept of normalization.',
            'What are indexes and when should they be used?',
            'How do you optimize a slow query?',
            'What is the difference between DELETE and TRUNCATE?'
        ],
        'HTML': [
            'What is the difference between div and span?',
            'Explain the concept of semantic HTML.',
            'What are the new features in HTML5?',
            'How do you optimize images for web?',
            'What is the purpose of meta tags?'
        ],
        'CSS': [
            'What is the difference between display: none and visibility: hidden?',
            'Explain the concept of CSS specificity.',
            'What are CSS preprocessors?',
            'How do you create a responsive design?',
            'What is the difference between position: relative and position: absolute?'
        ],
        'Django': [
            'What is the difference between GET and POST?',
            'Explain the concept of middleware.',
            'How does Django handle database migrations?',
            'What is the purpose of Django forms?',
            'How do you implement user authentication?'
        ],
        'Flask': [
            'What is the difference between Flask and Django?',
            'How do you handle database connections in Flask?',
            'Explain the concept of Flask blueprints.',
            'How do you implement user authentication?',
            'What is the purpose of Flask extensions?'
        ],
        'React': [
            'What is the difference between props and state?',
            'Explain the concept of virtual DOM.',
            'What are React hooks?',
            'How do you handle forms in React?',
            'What is the purpose of Redux?'
        ],
        'Node': [
            'What is the event loop in Node.js?',
            'How do you handle asynchronous operations?',
            'What is the difference between require and import?',
            'How do you handle errors in Node.js?',
            'What is the purpose of middleware in Express?'
        ],
        'Machine Learning': [
            'What is the difference between supervised and unsupervised learning?',
            'Explain the concept of overfitting.',
            'What are the different types of clustering algorithms?',
            'How do you evaluate a machine learning model?',
            'What is the purpose of cross-validation?'
        ],
        'Data Analysis': [
            'What are the different types of data visualization?',
            'How do you handle missing data?',
            'What is the difference between correlation and causation?',
            'How do you identify outliers?',
            'What is the purpose of statistical significance?'
        ],
        'Git': [
            'What is the difference between git pull and git fetch?',
            'How do you resolve merge conflicts?',
            'What is the purpose of git rebase?',
            'How do you create and switch branches?',
            'What is the difference between git reset and git revert?'
        ],
        'Linux': [
            'What is the difference between soft link and hard link?',
            'How do you manage processes in Linux?',
            'What is the purpose of cron jobs?',
            'How do you manage file permissions?',
            'What is the difference between grep and find?'
        ],
        'AWS': [
            'What is the difference between EC2 and Lambda?',
            'How do you manage security groups?',
            'What is the purpose of S3?',
            'How do you handle auto-scaling?',
            'What is the difference between RDS and DynamoDB?'
        ],
        'Docker': [
            'What is the difference between container and image?',
            'How do you manage Docker volumes?',
            'What is the purpose of Docker Compose?',
            'How do you optimize Docker images?',
            'What is the difference between Docker and Kubernetes?'
        ],
        'Kubernetes': [
            'What is the difference between pod and deployment?',
            'How do you manage secrets?',
            'What is the purpose of services?',
            'How do you handle scaling?',
            'What is the difference between StatefulSet and Deployment?'
        ]
    }

    questions = []
    for skill in skills:
        if skill in skill_questions:
            # Get 2 random questions for each skill
            skill_questions_list = skill_questions[skill]
            selected_questions = random.sample(skill_questions_list, min(2, len(skill_questions_list)))
            for question in selected_questions:
                questions.append({
                    'skill': skill,
                    'question': question
                })
    
    # Shuffle the questions
    random.shuffle(questions)
    return questions

def resume_upload(request):
    extracted_skills = None
    error = None
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        ext = os.path.splitext(resume_file.name)[1].lower()
        temp_path = default_storage.save('tmp/' + resume_file.name, resume_file)
        file_path = os.path.join(settings.MEDIA_ROOT, temp_path)
        try:
            if ext == '.pdf':
                text = extract_text_from_pdf(file_path)
            elif ext in ['.doc', '.docx']:
                text = extract_text_from_docx(file_path)
            else:
                error = 'Unsupported file type.'
                text = ''
            if text:
                extracted_skills = extract_skills_from_text(text)
                # Store skills in session
                request.session['extracted_skills'] = extracted_skills
                # Generate questions based on skills
                questions = generate_questions_for_skills(extracted_skills)
                request.session['interview_questions'] = questions
        except Exception as e:
            error = f'Error processing file: {e}'
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
    return render(request, 'resume-upload.html', {'extracted_skills': extracted_skills, 'error': error})

def feedback(request):
    feedback_data = request.session.get('interview_feedback', {})
    return render(request, 'feedback.html', {'feedback_data': feedback_data})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('index')

def history(request):
    return render(request, 'history.html')

def profile(request):
    fullname = request.session.get('user_fullname', 'N/A')
    email = request.session.get('user_email', 'N/A')
    context = {
        'fullname': fullname,
        'email': email
    }
    return render(request, 'profile.html', context)

@csrf_exempt
def api_detect_emotion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data_url = data.get('image')
            
            if not image_data_url:
                return JsonResponse({'error': 'No image data provided'}, status=400)

            # Extract base64 data
            # Format is typically "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
            header, encoded = image_data_url.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            
            # Convert bytes to NumPy array and then to OpenCV image (BGR)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame_bgr is None:
                return JsonResponse({'error': 'Could not decode image'}, status=400)

            emotion = detect_emotion_from_frame(frame_bgr)
            return JsonResponse({'emotion': emotion})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error in api_detect_emotion: {e}")
            return JsonResponse({'error': f'Error processing image: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def evaluate_answer(question, answer):
    try:
        prompt = f"""
        You are an expert technical interviewer with an emphasis on understanding core concepts.
        Evaluate the following answer for the given question. Your goal is to determine if the user grasps the key principles, even if their wording differs from a textbook definition.
        
        Provide a detailed evaluation in JSON format with the following structure:
        {{
            "score": <score out of 10. Base this on conceptual understanding and coverage of critical aspects. Minor omissions or alternative phrasing for correct concepts should not heavily penalize the score. Deduct more significantly for factual inaccuracies or misunderstanding of core principles. Consider a score of 5-7 for answers that are generally correct but lack depth or miss some non-critical nuances, and 8-10 for comprehensive and accurate understanding. Reserve scores below 5 for significant errors or omissions. >,
            "key_points_covered": <list of key concepts from an ideal answer that were correctly addressed in the user's answer. Focus on the essence of these points. >,
            "missing_points": <list of important concepts from an ideal answer that were missing or inadequately explained in the user's answer. Distinguish between critical omissions and minor details. >,
            "feedback": <detailed feedback on the user's answer. Explain what was good, what could be improved, and specifically why points were deducted, referencing the conceptual understanding. If the user's answer is a valid alternative to a common answer, acknowledge it. >,
            "correctness_rating": <A qualitative rating: "Excellent", "Good", "Fair", "Needs Improvement", "Poor">,
            "ideal_answer_summary": <A concise summary of the core concepts that a strong ideal answer should cover. This is for your reference in evaluation and for the user's learning.>
        }}

        Question: {question}
        User's Answer: {answer}

        Instructions for Evaluation:
        1. First, formulate a concise summary of the ideal concepts for the given Question. This will be your `ideal_answer_summary`.
        2. Compare the User's Answer to your `ideal_answer_summary`.
        3. Identify `key_points_covered` by the user, focusing on conceptual alignment.
        4. Identify `missing_points`, prioritizing critical concepts over minor details.
        5. Provide constructive `feedback` explaining your reasoning. Highlight both strengths and areas for improvement.
        6. Assign a `score` based on the conceptual grasp and coverage of critical points, as described above.
        7. Determine a `correctness_rating`.

        Focus on fairness and conceptual accuracy over strict adherence to a single phrasing for the ideal answer.
        """

        response = model.generate_content(prompt)
        # Attempt to remove markdown and parse JSON
        cleaned_response_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        evaluation = json.loads(cleaned_response_text)
        return evaluation
    except Exception as e:
        print(f"Error in evaluation: {str(e)}")
        print(f"Problematic Gemini response: {response.text if 'response' in locals() else 'Response not available'}")
        return {
            "score": 0,
            "key_points_covered": [],
            "missing_points": ["Error in evaluation process"],
            "feedback": "There was an error evaluating your answer. Please try again.",
            "correctness_rating": "Error",
            "ideal_answer_summary": "Could not retrieve ideal answer summary due to an evaluation error."
        }

def submit_answers(request):
    if request.method == 'POST':
        try:
            answers = request.POST.getlist('answers[]')
            questions = request.session.get('interview_questions', [])
            
            if not questions or len(answers) != len(questions):
                return JsonResponse({'error': 'Invalid submission'}, status=400)
            
            feedback_list = []
            total_score = 0
            
            for question_data, user_answer in zip(questions, answers):
                evaluation = evaluate_answer(question_data['question'], user_answer)
                
                feedback_list.append({
                    'question': question_data['question'],
                    'skill': question_data['skill'],
                    'answer': user_answer,
                    'score': evaluation.get('score', 0),
                    'key_points_covered': evaluation.get('key_points_covered', []),
                    'missing_points': evaluation.get('missing_points', []),
                    'feedback': evaluation.get('feedback', "Evaluation not available."),
                    'correctness_rating': evaluation.get('correctness_rating', "N/A"),
                    'ideal_answer_summary': evaluation.get('ideal_answer_summary', "Summary not available."),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                total_score += evaluation.get('score', 0)
            
            average_score = total_score / len(questions) if questions else 0
            
            request.session['interview_feedback'] = {
                'feedback_list': feedback_list,
                'average_score': round(average_score, 2),
                'total_questions': len(questions),
                'submission_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Answers submitted successfully',
                'redirect': '/feedback/'
            })
            
        except Exception as e:
            print(f"Error in submit_answers: {str(e)}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400) 