# **Profit Ex**

**Profit Ex** is a Flask-based web app for companies to manage and track their incomes, expenses, salaries, and net profits, providing actionable insights and user-friendly data management features.

## Features

- Dashboard for real-time data analysis.
- Income, expense, and salary tracking.
- Visualizations such as bar and pie charts for financial insights.
- PDF report generation for salary, income, and expense records.
- User authentication for secure access.
---

## **Technologies Used**
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **Charting Library:** Plotly
- **PDF Generation:** ReportLab

---
  
## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- MySQL (for database management)

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/nahid2003131/Profit-Ex.git
   cd profit-ex

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate     # For Windows

3. **Install Required Python Packages**

   ```bash
     pip install -r requirements.txt

3. **Configure the Database**

   ```bash
     app.config['MYSQL_HOST'] = 'localhost'
     app.config['MYSQL_USER'] = 'your_username'
     app.config['MYSQL_PASSWORD'] = 'your_password'
     app.config['MYSQL_DB'] = 'profitex'
   
4. **Start the Application**

   ```bash
     python app.py
## Screenshots
![Screenshot_3](https://github.com/user-attachments/assets/a7609420-1136-4dbe-b8fe-fa4880e4b49d)
![Screenshot_2](https://github.com/user-attachments/assets/41e01682-4935-4963-b908-72c37308a242)
![Screenshot_4](https://github.com/user-attachments/assets/ec13e219-fef7-4d5f-a371-09ff509012e0)
![Screenshot_5](https://github.com/user-attachments/assets/081b8465-5921-4dc2-a9a4-1b5bc0af8b73)
![Screenshot_6](https://github.com/user-attachments/assets/71e9147e-87fd-4dc9-9b6e-b0120bf21817)


   
