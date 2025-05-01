# german-phrases-learner
German Phrase Learner is a web-based application designed to help users learn German phrases through an interactive interface. Built with Flask, this app allows users to register, log in, and practice translating phrases from English to German with a pronunciation guide. It features multiple learning modes with time limits, a responsive design for mobile and desktop, and a timer that tracks progress without resetting on page changes. Users can save translations, copy phrases to the clipboard, and recover passwords via email.

# Features
User authentication (login, register, password recovery)
Multiple learning modes (Free, Basic, Medium, Hard, Expert, Insane) with configurable time limits
Responsive design with two-column layout for phrases
Persistent timer across page navigation
Save translations per user
Copy phrases to clipboard
Log timeout events to a file

# Technologies Used
Backend: Flask (Python)
Frontend: HTML, CSS, JavaScript
Storage: JSON files for users, phrases, and translations
Deployment: Local server (extendable to production with WSGI)

# Setup Instructions
Clone the repository:

```bash
git clone https://github.com/yourusername/german-phrase-learner.git
cd german-phrase-learner~~~
```
#Install dependencies:

```bash
pip install -r requirements.txt
```

*Ensure users.json and phrases.json are present in the project root (or create empty ones: {} and []).
Configure email settings in app.py for password recovery (update SMTP credentials).*

#Run the application:

```bash
python app.py
```
---
Access the app at *localhost:5000*
---

# Contributing
Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes.

# License
This project is licensed under the MIT License.
