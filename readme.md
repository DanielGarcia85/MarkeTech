# MarkeTech

**MarkeTech** is a job search and recruitment platform designed to connect job seekers with employers, developed as a final project at **HEG Arc Neuchâtel**, **HEG Genève**, **HES-SO Valais**. The platform combines a modern **Vue.js** frontend with a robust **Django** backend.

Link to our code committed to GitHub : https://github.com/heg-interschool/g-06-marketech

## Features

### For Job Seekers

- 📝 Professional Profile Management
- 📄 CV & Document Upload
- 🔍 Advanced Job Search
- 📱 Mobile-Responsive Interface
- 💬 Real-time Messaging with Employers
- ⭐ Job Favorites System
- 📊 Application Tracking
- ⭐ Premium Features Access

### For Employers

- 👔 Company Profile Management
- 📢 Job Posting Management
- 👥 Candidate Management
- 📨 Application Processing
- 📅 Interview Scheduling
- 💬 Messaging System
- 🌟 Premium Account Benefits

## Tech Stack

- **Frontend**: Vue.js 3 + Vite
- **Backend**: Django REST Framework
- **Database**: SQLite (development)
- **Authentication**: Django Allauth Headless
- **Storage**: Django Storage
- **UI Components**: Custom Vue Components

## Prerequisites

Ensure you have installed:

- **Node.js**: [Download here](https://nodejs.org/fr)
- **Python 3.10 or later**: [Download here](https://www.python.org/downloads/)
- **pip**: [Download here](https://pypi.org/project/pip/)
- **Django 4.x**: [Installation guide](https://www.djangoproject.com/)
- **Vue.js 3.x**: [Installation guide](https://vuejs.org/guide/quick-start.html)

## Installation

1.  **Clone the repository**:

```bash
git  clone  https://github.com/heg-interschool/g-06-marketech.git
cd  g-06-marketech
```

2.  **Setup Backend**:

```bash
# Create virtual environment
python  -m  venv  venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source  venv/bin/activate

# Install dependencies and setup the application
python manage.py initial_setup
```

3.  **Run Backend** :

```bash
python manage.py runserver
```

4.  **Setup Frontend**:

```bash
npm  install
```

5.  **Run Frontend**:

```bash
npm run dev
```

**Access the application at**:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Admin Interface: http://localhost:8000/api/admin/

## Project Structure

| Directory         | Content                        |
| ----------------- | ------------------------------ |
| `/backend`        | Django Project & API           |
| `/src/components` | Vue Reusable Components        |
| `/src/views`      | Vue Views/Pages                |
| `/src/services`   | API Services & Business Logic  |
| `/src/assets`     | Static Assets (images, styles) |
| `/public`         | Public Static Files            |

## License

This project is licensed under the _Creative Commons Attribution-ShareAlike (CC BY-SA)_ license.

### Author

Project created by **Team 6 : MarkeTech** as part of the **65-41 Common module - Inter-school Software Development** course at **Haute École de Gestion Genève**, **Haute école de gestion Arc Neuchâtel** and **HES-SO Valais** during the Spring semester of 2025.

#### Contributors

- Jonathan Borel-Jaquet
- Daniel Garcia
- Ysias Hummel
- Alexis Jordan
