from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hr_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class JobTitles(db.Model):
    __tablename__ = 'JobTitles'
    JobTitleID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    JobTitleName = db.Column(db.String(100), nullable=False, unique=True)
    MinSalary = db.Column(db.Numeric(10, 2), nullable=False)
    MaxSalary = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    employees = db.relationship('Employees', backref='job_title', lazy=True)

class Departments(db.Model):
    __tablename__ = 'Departments'
    DepartmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DepartmentName = db.Column(db.String(100), nullable=False, unique=True)
    Location = db.Column(db.String(100), nullable=False)
    HeadID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=True)
    
    # Relationships
    employees = db.relationship('Employees', backref='department', lazy=True)
    projects = db.relationship('Projects', backref='department', lazy=True)
    department_head = db.relationship('Employees', foreign_keys=[HeadID], backref='headed_departments')

class Employees(db.Model):
    __tablename__ = 'Employees'
    EmployeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Gender = db.Column(db.String(1), nullable=False)
    DOB = db.Column(db.Date, nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Phone = db.Column(db.String(20), nullable=True)
    HireDate = db.Column(db.Date, nullable=False)
    JobTitleID = db.Column(db.Integer, db.ForeignKey('JobTitles.JobTitleID'), nullable=False)
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Departments.DepartmentID'), nullable=False)
    ManagerID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=True)
    Salary = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    managed_employees = db.relationship('Employees', backref=db.backref('manager', remote_side=[EmployeeID]))
    employee_projects = db.relationship('EmployeeProjects', backref='employee', lazy=True)
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    leave_requests = db.relationship('LeaveRequests', backref='employee', lazy=True)
    performance_reviews = db.relationship('PerformanceReviews', backref='employee', lazy=True)
    payroll_records = db.relationship('Payroll', backref='employee', lazy=True)

class Projects(db.Model):
    __tablename__ = 'Projects'
    ProjectID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProjectName = db.Column(db.String(200), nullable=False)
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Departments.DepartmentID'), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=True)
    Budget = db.Column(db.Numeric(12, 2), nullable=True)
    
    # Relationships
    employee_projects = db.relationship('EmployeeProjects', backref='project', lazy=True)

class EmployeeProjects(db.Model):
    __tablename__ = 'EmployeeProjects'
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), primary_key=True)
    ProjectID = db.Column(db.Integer, db.ForeignKey('Projects.ProjectID'), primary_key=True)
    Role = db.Column(db.String(100), nullable=False)
    AllocationPercent = db.Column(db.Numeric(5, 2), default=100.00)

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    AttendanceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=False)
    Date = db.Column(db.Date, nullable=False)
    CheckInTime = db.Column(db.Time, nullable=True)
    CheckOutTime = db.Column(db.Time, nullable=True)
    Status = db.Column(db.String(20), nullable=False)

class LeaveRequests(db.Model):
    __tablename__ = 'LeaveRequests'
    LeaveID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    LeaveType = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(20), default='Pending')
    ApprovedBy = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=True)
    
    # Relationships
    approver = db.relationship('Employees', foreign_keys=[ApprovedBy], backref='approved_leaves')

class PerformanceReviews(db.Model):
    __tablename__ = 'PerformanceReviews'
    ReviewID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=False)
    ReviewerID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=False)
    ReviewDate = db.Column(db.Date, nullable=False)
    Rating = db.Column(db.Integer, nullable=False)
    Comments = db.Column(db.Text, nullable=True)
    
    # Relationships
    reviewer = db.relationship('Employees', foreign_keys=[ReviewerID], backref='conducted_reviews')

class Payroll(db.Model):
    __tablename__ = 'Payroll'
    PayrollID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=False)
    Month = db.Column(db.Integer, nullable=False)
    Year = db.Column(db.Integer, nullable=False)
    BasicSalary = db.Column(db.Numeric(10, 2), nullable=False)
    Allowances = db.Column(db.Numeric(10, 2), default=0.00)
    Deductions = db.Column(db.Numeric(10, 2), default=0.00)
    NetSalary = db.Column(db.Numeric(10, 2), nullable=False)

# Utility functions
def get_employee_full_name(employee):
    """Get full name of employee"""
    return f"{employee.FirstName} {employee.LastName}"

def format_currency(amount):
    """Format currency amount"""
    if amount is None:
        return "$0.00"
    return f"${float(amount):,.2f}"

def format_date(date_obj):
    """Format date object"""
    if date_obj is None:
        return "N/A"
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime('%Y-%m-%d')

def format_time(time_obj):
    """Format time object"""
    if time_obj is None:
        return "N/A"
    if isinstance(time_obj, str):
        return time_obj
    return time_obj.strftime('%H:%M:%S')

# Context processors for templates
@app.context_processor
def utility_processor():
    return {
        'get_employee_full_name': get_employee_full_name,
        'format_currency': format_currency,
        'format_date': format_date,
        'format_time': format_time
    }

# Basic route for testing
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Database Management System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .info { background: #ecf0f1; padding: 20px; border-radius: 5px; }
            .warning { background: #f39c12; color: white; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>HR Database Management System</h1>
            <div class="info">
                <h2>System Status: Ready</h2>
                <p>This is a Flask-based HR database management system with CLI interface.</p>
                <p><strong>Database:</strong> SQLite (hr_database.db)</p>
                <p><strong>Tables:</strong> 9 core tables with complete relationships</p>
                <p><strong>CLI Interface:</strong> Use <code>python hr_cli.py</code> to access the system</p>
            </div>
            <div class="warning">
                <h3>Important:</h3>
                <p>This is a CLI-based system. Use the command line interface for all operations.</p>
                <p>Run: <code>python hr_cli.py --help</code> to see available commands.</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("HR Database Management System initialized!")
    print("Database tables created successfully.")
    print("Use 'python hr_cli.py' to access the CLI interface.")
    app.run(debug=True, host='0.0.0.0', port=5000)
