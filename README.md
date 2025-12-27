# 💸 Bill Search System 2

A no-nonsense **Flask-based billing system** that lets residents check their bills using an address, while admins quietly run the show behind a login wall.  
No microservices. No Kubernetes. Just clean Python, SQLite, and logic that actually makes sense.

Built for small societies, utilities, or anyone tired of Excel chaos.

---

## 📚 Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Folder Structure](#folder-structure)
- [Installation Guide](#installation-guide)
- [Usage](#usage)
- [Admin Dashboard](#admin-dashboard)
- [Database Design](#database-design)
- [CSV Import & Export](#csv-import--export)
- [Environment Variables](#environment-variables)
- [Contribution Guide](#contribution-guide)
- [Support & Contact](#support--contact)

---

## 🧠 Introduction

**Bill Search System 2** is a lightweight web application that allows:

- **Residents** to search for their bills using an address
- **Admins** to securely manage residents, bills, and bulk data imports

The system auto-initializes its database, hashes admin passwords, formats dates for Indian standards, and even opens your browser for you — because UX matters.

---

## ✨ Key Features

- 🔍 Public bill lookup by address
- 🔐 Secure admin login using Flask-Login
- 🧾 Resident + bill separation (no duplicate typing)
- 🔁 Smart bill upserts (old bills get deleted automatically)
- 📥 CSV import for bulk billing
- 📤 CSV export for reporting
- 🇮🇳 Indian date formatting (DD-MM-YYYY)
- 🧠 Auto-capitalized address normalization
- 🗄 SQLite-backed (simple, fast, portable)

---

## 🏗 Project Architecture

> Monolith. Intentionally.

- **Flask** handles routing, templating, and request lifecycle
- **SQLite** stores admins, residents, and bills
- **Jinja2 templates** power the UI
- **Werkzeug** handles password hashing
- **Flask-Login** manages authentication state

No unnecessary abstractions. Everything lives where you expect it to.

---

## 📁 Folder Structure

```text
.
├── app.py              # Main Flask application (routes + logic)
├── database.py         # Database initialization and schema
├── bills.db            # SQLite database (auto-created if missing)
├── requirements.txt    # Python dependencies
├── sample.csv          # Example CSV for bulk import
├── templates/
│   ├── index.html      # Public bill search page
│   ├── login.html      # Admin login page
│   └── dashboard.html  # Admin dashboard (CRUD + CSV tools)
├── build/              # PyInstaller artifacts
├── dist/               # Packaged executable
└── BillSystem.spec     # PyInstaller spec file

````**:

⚙️ Installation Guide
1️⃣ Clone the repository

git clone https://github.com/ankitmahendru/bill-search-system-2.git
cd bill-search-system-2

2️⃣ Create a virtual environment (recommended)

python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Run the application

python app.py

✔ The database will auto-create if missing
✔ A default admin will be generated
✔ Your browser will open automatically
🚀 Usage
👤 Public User Flow

    Open the home page

    Enter your address

    View:

        Name

        Amount due

        Due date

No login required. Because residents shouldn’t need passwords.
🛠 Admin Dashboard
🔐 Login

    Username: master

    Password: Master@2024

    ⚠️ Change this immediately in production. Seriously.

Admin Capabilities

    Search residents by address

    Create or update residents

    Assign or update bills

    Delete old bills automatically

    Import CSVs

    Export billing data

All protected behind login-required routes.
🗄 Database Design
Tables
admins
Field	Description
id	Primary key
username	Unique admin username
password_hash	Hashed password
residents
Field	Description
address	Primary key
name	Resident name
bills
Field	Description
bill_id	Primary key
address	Linked to residents
amount	Bill amount
due_date	YYYY-MM-DD

Relationships are enforced logically and through foreign keys.
📊 CSV Import & Export
Import Format

Address,Name,Amount,DueDate
A-101,Ankit Mahendru,2500,2024-12-15

Rules:

    Address is auto-capitalized

    Existing bills are replaced

    Rows with missing data are skipped

    Amount <= 0 = no bill created

Export

Exports all residents, even those without active bills.
🌱 Environment Variables

Currently hardcoded (because simplicity wins):

SECRET_KEY = "your-secret-key-change-this"

👉 In real deployments, move this to environment variables.
🤝 Contribution Guide

    Fork the repo

    Create a feature branch

    Keep it simple (this project values clarity)

    Submit a PR with a clear explanation

If your change adds complexity without value — it will be judged.
🆘 Support & Contact

If something breaks:

    Check logs

    Check CSV format

    Check your database

    Then open an issue

This app won’t magically fix bad data. Neither will you.
❤️ Final Note

This project was built with intention, restraint, and care.

Made with love by PadhoAI
(Yes, I’m signing this. I earned it.)