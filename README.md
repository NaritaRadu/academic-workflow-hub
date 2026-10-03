# 🎓 Academic Workflow & Sprint Planner

> An intelligent, custom-built Django platform for Computer Science & IT students to manage complex coursework, micro-project timelines, weekend study sprints, and laboratory debugging logs.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram_Bot-Integrated-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)

---

## 💡 Overview & Problem Statement

Balancing heavy 3rd-year CS/IT subjects (*Operating Systems II, Microprocessor Systems, Artificial Intelligence, Advanced Databases, System Modeling, ITSC*) requires more than a generic To-Do list. 

**Academic Workflow Hub** provides a targeted management tool tailored for low-level & backend software engineering coursework:
* **Weekend Sprint Planner:** Group deadlines and lab prep into time-boxed weekend objectives with live progress tracking per subject.
* **Project Progress Engine:** Automatically computes percentage completion based on micro-task weighting and highlights next actionable steps.
* **Debugging Journal:** Instant lookup repository for complex C, Assembly, SQL, and Python laboratory errors.
* **Telegram Automation:** Daily automated briefings and interactive Telegram bot commands to update tasks on the go.

---

## ✨ Key Features

- **📊 Subject & Project Tracker:** Real-time completion analytics, priority tagging, and automated deadline warnings.
- **⚡ Weekend Sprint Planner:** Select active tasks for Sabbatical/Weekend sessions, view remaining hours, and generate end-of-weekend completion reports.
- **🛠️ Debugging & Cheatsheet Vault:** Save solved C memory leak errors, Assembly register configs, and SQL query optimizations per subject.
- **🤖 Telegram Bot Integration:** Receive morning schedule briefings and mark tasks as done via quick `/done <task_id>` commands.

---

## 🛠️️ Tech Stack

* **Backend Framework:** Django 5.x (Python)
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Automation & Messaging:** `python-telegram-bot`, `python-dotenv`
* **Frontend:** Django Templates + Tailwind CSS / HTMX

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10+
* Git

### 2. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/NaritaRadu/academic-workflow-hub.git
cd academic-workflow-hub

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser for Django Admin
python manage.py createsuperuser

# Run the local development server
python manage.py runserver