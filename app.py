# Importing necessary modules
from flask import Flask, render_template, redirect, request, session
from flask_mysqldb import MySQL
import json
import plotly.graph_objs as go
from flask import send_file, request
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io



app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'nahid'
app.config['MYSQL_DB'] = 'profitex'

# Initialize MySQL
mysql = MySQL(app)

# Create tables if not exists
def create_tables():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS salary (
                id INT  PRIMARY KEY,
                Name VARCHAR(50),
                Position VARCHAR(50),
                Salary INT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS expense (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source VARCHAR(50),
                amount INT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source VARCHAR(50),
                amount INT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        mysql.connection.commit()
        cur.close()

# Initialize table creation
create_tables()
#dashboard
@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' in session:
        cur = mysql.connection.cursor()

        # Fetch total salary
        cur.execute("SELECT SUM(Salary) FROM salary")
        total_salary = cur.fetchone()[0] or 0

        # Fetch total income
        cur.execute("SELECT SUM(amount) FROM income")
        total_income = cur.fetchone()[0] or 0

        # Fetch total expense
        cur.execute("SELECT SUM(amount) FROM expense")
        total_expense = cur.fetchone()[0] or 0

        # Add total salary to total expense
        total_expense += total_salary

        # Calculate net profit
        net_profit = total_income - total_expense

        # Create the bar chart data
        bar_chart_data = {
            'labels': ['Total Income', 'Total Expense', 'Net Profit'],
            'values': [total_income, total_expense, net_profit]
        }

        # Plotting the bar chart
        bar_chart = go.Bar(x=bar_chart_data['labels'], y=bar_chart_data['values'])

        # Define the layout for the bar chart
        bar_layout = go.Layout(
            title='Comparison of Total Income, Total Expense, and Net Profit',
            xaxis=dict(title='Category'),
            yaxis=dict(title='Amount')
        )

        # Create the bar chart figure
        bar_fig = go.Figure(data=[bar_chart], layout=bar_layout)

        # Create the pie chart data
        pie_chart_data = {
            'labels': ['Salary', 'Other Expenses'],
            'values': [total_salary, total_expense - total_salary]
        }

        # Plotting the pie chart
        pie_chart = go.Pie(labels=pie_chart_data['labels'], values=pie_chart_data['values'])

        # Define the layout for the pie chart
        pie_layout = go.Layout(
            title='Expense Distribution'
        )

        # Create the pie chart figure
        pie_fig = go.Figure(data=[pie_chart], layout=pie_layout)

        # Fetch data for the income bar chart
        cur.execute("SELECT source, amount FROM income")
        income_data = cur.fetchall()

        # Process the fetched data into lists for the income bar chart
        income_labels = [row[0] for row in income_data]
        income_values = [row[1] for row in income_data]

        # Plotting the income bar chart
        income_bar_chart = go.Bar(x=income_labels, y=income_values, name='Income')

        # Define the layout for the income bar chart
        income_bar_layout = go.Layout(
            title='Income Distribution',
            xaxis=dict(title='Description'),
            yaxis=dict(title='Amount')
        )

        # Create the income bar chart figure
        income_bar_fig = go.Figure(data=[income_bar_chart], layout=income_bar_layout)

        # Fetch data for the expense bar chart
        cur.execute("SELECT source, amount FROM expense")
        expense_data = cur.fetchall()

        # Process the fetched data into lists for the expense bar chart
        expense_labels = [row[0] for row in expense_data]
        expense_values = [row[1] for row in expense_data]

        # Plotting the expense bar chart
        expense_bar_chart = go.Bar(x=expense_labels, y=expense_values, name='Expense')

        # Define the layout for the expense bar chart
        expense_bar_layout = go.Layout(
            title='Expense Distribution',
            xaxis=dict(title='Description'),
            yaxis=dict(title='Amount')
        )

        # Create the expense bar chart figure
        expense_bar_fig = go.Figure(data=[expense_bar_chart], layout=expense_bar_layout)

        # Fetch data for the salary bar chart
        cur.execute("SELECT Name, Salary FROM salary")
        salary_data = cur.fetchall()

        # Process the fetched data into lists for the salary bar chart
        salary_names = [row[0] for row in salary_data]
        salary_values = [row[1] for row in salary_data]

        # Plotting the salary bar chart
        salary_bar_chart = go.Bar(x=salary_names, y=salary_values, name='Salary')

        # Define the layout for the salary bar chart
        salary_bar_layout = go.Layout(
            title='Salary Distribution',
            xaxis=dict(title='Name'),
            yaxis=dict(title='Salary')
        )

        # Create the salary bar chart figure
        salary_bar_fig = go.Figure(data=[salary_bar_chart], layout=salary_bar_layout)

        # Convert the Plotly figures to JSON format
        charts = {
            'bar_chart': json.loads(bar_fig.to_json()),
            'pie_chart': json.loads(pie_fig.to_json()),
            'income_bar_chart': json.loads(income_bar_fig.to_json()),
            'expense_bar_chart': json.loads(expense_bar_fig.to_json()),
            'salary_bar_chart': json.loads(salary_bar_fig.to_json())
        }

        return render_template('index.html', charts=charts)
    else:
        return redirect("/login")


# Route for salary
@app.route("/salary", methods=["GET", "POST"])
def salary():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, Name, Position, Salary FROM salary")
        tasks = cur.fetchall()
        
        cur.execute("SELECT SUM(Salary) FROM salary")
        total_result = cur.fetchone()
        total = total_result[0] if total_result else 0  
        cur.close()

        tasks = [{'id': task[0], 'Name': task[1], 'Position': task[2], 'Salary': task[3]} for task in tasks]
        return render_template('salary.html', tasks=tasks, total=total)
    else:
        return redirect("/login")


@app.route("/download_pdf/<string:report_type>", methods=["GET"])
def download_pdf(report_type):
    if 'username' in session:
        # Prepare data based on the report type
        table_data = []
        title = ""

        if report_type == "salary":
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, Name, Position, Salary FROM salary")
            tasks = cur.fetchall()
            cur.close()
            table_data = [["S.No", "Name", "Position", "Salary In taka"]]
            table_data.extend([[i + 1, task[1], task[2], task[3]] for i, task in enumerate(tasks)])
            title = "Salary Report"

        elif report_type == "income":
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, source, amount FROM income")
            tasks = cur.fetchall()
            cur.close()
            table_data = [["S.No", "Source", "Amount ($)"]]
            table_data.extend([[i + 1, task[1], task[2]] for i, task in enumerate(tasks)])
            title = "Income Report"

        elif report_type == "expense":
            cur = mysql.connection.cursor()
            cur.execute("SELECT id,source, amount FROM expense")
            tasks = cur.fetchall()
            cur.close()
            table_data = [["S.No", "Category", "Amount ($)"]]
            table_data.extend([[i + 1, task[1], task[2]] for i, task in enumerate(tasks)])
            title = "Expense Report"

        else:
            return "Invalid report type!", 400

        # Create PDF in memory
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add Title
        styles = getSampleStyleSheet()
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))

        # Create Table
        col_widths = [50, 200, 150, 100] if report_type == "salary" else [50, 200, 150]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color to black
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all text
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for header
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # Header font size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  # Padding for header
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # Data font size
        ]))
        elements.append(table)

        # Build PDF
        pdf.build(elements)
        buffer.seek(0)

        # Return PDF as a response
        filename = f"{report_type}_report.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")
    else:
        return redirect("/login")

# Route for the expense
@app.route("/expense", methods=["GET", "POST"])
def expense():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, source, amount FROM expense")
        tasks = cur.fetchall()
        
        cur.execute("SELECT SUM(amount) FROM expense")
        total_result = cur.fetchone()
        total_expense = total_result[0] if total_result else 0  
        cur.close()

        tasks = [{'id': task[0], 'source': task[1], 'amount': task[2]} for task in tasks]
        return render_template('expense.html', tasks=tasks, total_expense=total_expense)
    else:
        return redirect("/login")
    

# Route for the income
@app.route("/income", methods=["GET", "POST"])
def income():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, source, amount FROM income")
        tasks = cur.fetchall()
        
        cur.execute("SELECT SUM(amount) FROM income")
        total_result = cur.fetchone()
        total_income = total_result[0] if total_result else 0  
        cur.close()

        tasks = [{'id': task[0], 'source': task[1], 'amount': task[2]} for task in tasks]
        return render_template('income.html', tasks=tasks, total_income=total_income)
    else:
        return redirect("/login")

# Define route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['login-username']  # Updated to match HTML input names
        password = request.form['login-pass']  # Updated to match HTML input names
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cur.fetchone()
        cur.close()
        if admin:
            session['username'] = username
            return redirect("/")
        else:
            return render_template('login.html', error="Invalid username or password.")
    else:
        return render_template('login.html', error="")

# Route for adding a new employee
@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if 'username' in session:
        if request.method == "POST":
            employee_id = request.form['employee_id']
            name = request.form['name']
            position = request.form['position']
            salary = request.form['salary']
            
            # Check if salary is a valid integer
            try:
                salary = int(salary)
            except ValueError:
                message = "Salary must be a valid integer."
                return render_template('add_employee.html', message=message)
            
            cur = mysql.connection.cursor()
            # Check if employee ID already exists
            cur.execute("SELECT * FROM salary WHERE id = %s", (employee_id,))
            if cur.fetchone():
                message = "Employee ID already exists. Please choose another ID."
                cur.close()
                return render_template('add_employee.html', message=message)
            else:
                cur.execute("INSERT INTO salary (id, Name, Position, Salary) VALUES (%s, %s, %s, %s)", (employee_id, name, position, salary))
                mysql.connection.commit()
                cur.close()
                return redirect("/salary")  # Redirect to the dashboard after adding the employee
        else:
            return render_template('add_employee.html')
    else:
        return redirect("/login")


# Route for editing an employee
@app.route("/edit_employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):
    if 'username' in session:
        cur = mysql.connection.cursor()
        if request.method == "POST":
            name = request.form['name']
            position = request.form['position']
            salary = request.form['salary']
            cur.execute("UPDATE salary SET Name=%s, Position=%s, Salary=%s WHERE id=%s", (name, position, salary, id))
            mysql.connection.commit()
            cur.close()
            return redirect("/salary")
        else:
            cur.execute("SELECT id, Name, Position, Salary FROM salary WHERE id = %s", (id,))
            employee = cur.fetchone()
            cur.close()
            if employee:
                employee = {'id': employee[0], 'Name': employee[1], 'Position': employee[2], 'Salary': employee[3]}
                return render_template('edit_employee.html', employee=employee)
            else:
                return redirect("/salary")
    else:
        return redirect("/login")

# Route for deleting an employee
@app.route("/delete_employee/<int:id>")
def delete_employee(id):
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM salary WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect("/salary")
    else:
        return redirect("/login")

# Route for deleting an employee
@app.route("/delete_task/<int:id>")
def delete_task(id):
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM expense WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect("/expense")
    else:
        return redirect("/login")

# Route for logout
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/login")
    
    
    
# Route for editing an expense
@app.route("/edit_expense/<int:id>", methods=["GET", "POST"])
def edit_expense(id):
    if 'username' in session:
        cur = mysql.connection.cursor()
        if request.method == "POST":
            source = request.form['source']
            amount = request.form['amount']
            cur.execute("UPDATE expense SET source=%s, amount=%s WHERE id=%s", (source, amount, id))
            mysql.connection.commit()
            cur.close()
            return redirect("/expense")
        else:
            cur.execute("SELECT id, source, amount FROM expense WHERE id = %s", (id,))
            expense = cur.fetchone()
            cur.close()
            if expense:
                expense = {'id': expense[0], 'source': expense[1], 'amount': expense[2]}
                return render_template('edit_expense.html', expense=expense)
            else:
                return redirect("/expense")
    else:
        return redirect("/login")

# Route for adding a new expense
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if 'username' in session:
        if request.method == "POST":
            source = request.form['source']
            amount = request.form['amount']
            
            # Check if amount is a valid integer
            try:
                amount = int(amount)
            except ValueError:
                message = "Amount must be a valid integer."
                return render_template('add_expense.html', message=message)
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO expense (source, amount) VALUES (%s, %s)", (source, amount))
            mysql.connection.commit()
            cur.close()
            return redirect("/expense")
        else:
            return render_template('add_expense.html')
    else:
        return redirect("/login")
    
# Route for deleting an income
@app.route("/delete_income/<int:id>")
def delete_income(id):
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM income WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect("/income")
    else:
        return redirect("/login")
# Route for editing an income
@app.route("/edit_income/<int:id>", methods=["GET", "POST"])
def edit_income(id):
    if 'username' in session:
        cur = mysql.connection.cursor()
        if request.method == "POST":
            source = request.form['source']
            amount = request.form['amount']
            cur.execute("UPDATE income SET source=%s, amount=%s WHERE id=%s", (source, amount, id))
            mysql.connection.commit()
            cur.close()
            return redirect("/income")
        else:
            cur.execute("SELECT id, source, amount FROM income WHERE id = %s", (id,))
            income = cur.fetchone()
            cur.close()
            if income:
                income = {'id': income[0], 'source': income[1], 'amount': income[2]}
                return render_template('edit_income.html', income=income)
            else:
                return redirect("/income")
    else:
        return redirect("/login")
# Route for adding a new income
@app.route("/add_income", methods=["GET", "POST"])
def add_income():
    if 'username' in session:
        if request.method == "POST":
            source = request.form['source']
            amount = request.form['amount']
            
            # Check if amount is a valid integer
            try:
                amount = int(amount)
            except ValueError:
                message = "Amount must be a valid integer."
                return render_template('add_income.html', message=message)
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO income (source, amount) VALUES (%s, %s)", (source, amount))
            mysql.connection.commit()
            cur.close()
            return redirect("/income")
        else:
            return render_template('add_income.html')
    else:
        return redirect("/login")


# Run the app if executed directly
if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
