IntervuAI 💼🤖
IntervuAI is a full-stack AI-powered interview preparation platform built with Django that simulates real-world hiring processes. It is designed to help users assess, enhance, and perfect their job-readiness by providing personalized feedback across multiple dimensions like resume quality, technical skills, communication ability, and overall confidence.

✨ Key Features

📄 Resume Analyzer (ATS-Based)
Upload resumes via resume-upload.html.
Analyze compatibility based on job title, keywords, and formatting.
Visual feedback and recommendations provided in feedback.html.

🤖 Mock Interview Simulation
Conduct simulated interviews using interview.html and start-interview.html.
Emotion detection using:
emotion_detector.py
model (1).h5
haarcascade_frontalface_default.xml
Microphone and camera used to monitor expressions and audio responses.

📊 Feedback System
Evaluation based on:
Tone, fluency, and confidence.
Facial expression and gesture analysis.
Feedback shown in feedback.html and dashboard.html.

📜 User Management
User registration (signup.html) and profiles (profile.html).
Interview and resume history (history.html).

🔗 Navigation
base.html used for consistent layout across all pages.
Routing configured in urls.py.

🛠️ Tech Stack

Frontend: HTML, CSS, JavaScript (interactive UI)

Backend: Django, Python
AI/ML: NLP for question generation, Deep Learning for video/audio analysis
APIs Used: Monster Jobs API, Resume Parser, OpenCV, SpeechRecognition
Database: SQLite / PostgreSQL
Others: Webcam access, Graph generation (matplotlib, seaborn)


🚀 Getting Started
Prerequisites
Python 3.8+

pip (Python package installer)

Django

OpenCV, SpeechRecognition, PyAudio, NLTK, matplotlib, etc.

Installation
bash
Copy code
git clone [https://github.com/yourusername/intervuai.git](https://github.com/Shivani901/IntrvuAI/)
cd intervuai
pip install -r requirements.txt
python manage.py runserver

📂 Project Structure
cpp
NEWPROJECT1/
│
├── interview_platform/               # Main Django app for settings and routing
│   ├── emotion_detector.py           # Emotion detection logic using OpenCV and Deep Learning
│   ├── settings.py, urls.py, wsgi.py
│
├── newproject1/                      # Legacy or initial project files
│   ├── *.html                        # Early-stage HTML files (might be migrated to templates/)
│   ├── model (1).h5                  # Trained emotion detection model
│   ├── haarcascade_frontalface...   # Face detection XML for OpenCV
│
├── templates/                        # Django HTML templates
│   ├── index.html, dashboard.html...
│
├── static/                           # Static assets (CSS/JS)
│   ├── css/styles.css
│   └── js/script.js
│
├── db.sqlite3                        # SQLite database
└── manage.py      

📈 Future Enhancements
Real-time mock interviews with live mentors.
Multilingual support.
Resume templates and builder.
Integration with job portals (LinkedIn, Indeed).

🤝 Contributing
Feel free to fork the repo and raise a pull request with improvements, bug fixes, or new features.

📧 Contact
Shivani Kewat
Email: [shivanikewat5175@gmail.com]
