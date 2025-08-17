#!/usr/bin/env python3
"""
HR Database Management System - Database Initialization Script
This script initializes the database and loads sample data.
"""

import sqlite3
import os
from datetime import datetime, date, time

def init_database():
    """Initialize the database with schema and sample data"""
    
    # Remove existing database if it exists
    if os.path.exists('hr_database.db'):
        os.remove('hr_database.db')
        print("Removed existing database.")
    
    # Create new database connection
    conn = sqlite3.connect('hr_database.db')
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Read and execute schema
    try:
        with open('schema.sql', 'r') as schema_file:
            schema_sql = schema_file.read()
            cursor.executescript(schema_sql)
        print("✓ Database schema created successfully.")
    except FileNotFoundError:
        print("❌ Error: schema.sql file not found!")
        return False
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False
    
    print("Loading sample data...")
    
    # Read and execute sample data
    try:
        with open('data.sql', 'r') as data_file:
            data_sql = data_file.read()
            cursor.executescript(data_sql)
        print("✓ Sample data loaded successfully.")
    except FileNotFoundError:
        print("❌ Error: data.sql file not found!")
        return False
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✓ Database initialization completed successfully!")
    return True

def verify_database():
    """Verify that the database was created correctly"""
    
    if not os.path.exists('hr_database.db'):
        print("❌ Database file not found!")
        return False
    
    conn = sqlite3.connect('hr_database.db')
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        'JobTitles', 'Departments', 'Employees', 'Projects', 
        'EmployeeProjects', 'Attendance', 'LeaveRequests', 
        'PerformanceReviews', 'Payroll'
    ]
    
    print("\nVerifying database structure...")
    for table in expected_tables:
        if table in tables:
            print(f"✓ {table} table exists")
        else:
            print(f"❌ {table} table missing!")
    
    # Check record counts
    print("\nChecking record counts...")
    for table in expected_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✓ {table}: {count} records")
        except Exception as e:
            print(f"❌ Error counting {table}: {e}")
    
    # Check some sample data
    print("\nChecking sample data...")
    
    # Check employees
    cursor.execute("SELECT COUNT(*) FROM Employees")
    emp_count = cursor.fetchone()[0]
    if emp_count >= 10:
        print(f"✓ Employees: {emp_count} records (minimum 10 required)")
    else:
        print(f"❌ Employees: {emp_count} records (minimum 10 required)")
    
    # Check departments
    cursor.execute("SELECT COUNT(*) FROM Departments")
    dept_count = cursor.fetchone()[0]
    if dept_count >= 10:
        print(f"✓ Departments: {dept_count} records (minimum 10 required)")
    else:
        print(f"❌ Departments: {dept_count} records (minimum 10 required)")
    
    # Check projects
    cursor.execute("SELECT COUNT(*) FROM Projects")
    proj_count = cursor.fetchone()[0]
    if proj_count >= 10:
        print(f"✓ Projects: {proj_count} records (minimum 10 required)")
    else:
        print(f"❌ Projects: {proj_count} records (minimum 10 required)")
    
    # Check relationships
    print("\nChecking relationships...")
    
    # Check if employees have valid job titles
    cursor.execute("""
        SELECT COUNT(*) FROM Employees e 
        LEFT JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID 
        WHERE jt.JobTitleID IS NULL
    """)
    invalid_jobs = cursor.fetchone()[0]
    if invalid_jobs == 0:
        print("✓ All employees have valid job titles")
    else:
        print(f"❌ {invalid_jobs} employees have invalid job titles")
    
    # Check if employees have valid departments
    cursor.execute("""
        SELECT COUNT(*) FROM Employees e 
        LEFT JOIN Departments d ON e.DepartmentID = d.DepartmentID 
        WHERE d.DepartmentID IS NULL
    """)
    invalid_depts = cursor.fetchone()[0]
    if invalid_depts == 0:
        print("✓ All employees have valid departments")
    else:
        print(f"❌ {invalid_depts} employees have invalid departments")
    
    conn.close()
    return True

def run_sample_queries():
    """Run some sample queries to verify functionality"""
    
    print("\nRunning sample queries to verify functionality...")
    
    conn = sqlite3.connect('hr_database.db')
    cursor = conn.cursor()
    
    # Sample query 1: Count employees by department
    print("\n1. Employee count by department:")
    cursor.execute("""
        SELECT d.DepartmentName, COUNT(e.EmployeeID) as EmployeeCount
        FROM Departments d
        LEFT JOIN Employees e ON d.DepartmentID = e.DepartmentID
        GROUP BY d.DepartmentID, d.DepartmentName
        ORDER BY EmployeeCount DESC
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} employees")
    
    # Sample query 2: Average salary by job title
    print("\n2. Average salary by job title:")
    cursor.execute("""
        SELECT jt.JobTitleName, ROUND(AVG(e.Salary), 2) as AverageSalary
        FROM JobTitles jt
        LEFT JOIN Employees e ON jt.JobTitleID = e.JobTitleID
        GROUP BY jt.JobTitleID, jt.JobTitleName
        ORDER BY AverageSalary DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0]}: ${row[1]:,.2f}")
    
    # Sample query 3: Project budget summary
    print("\n3. Project budget summary:")
    cursor.execute("""
        SELECT p.ProjectName, p.Budget, COUNT(ep.EmployeeID) as TeamSize
        FROM Projects p
        LEFT JOIN EmployeeProjects ep ON p.ProjectID = ep.ProjectID
        GROUP BY p.ProjectID, p.ProjectName, p.Budget
        ORDER BY p.Budget DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        budget = row[1] if row[1] else 0
        print(f"   {row[0]}: ${budget:,.2f} (Team: {row[2]} people)")
    
    conn.close()

def main():
    """Main function to initialize the database"""
    
    print("=" * 60)
    print("HR Database Management System - Database Initialization")
    print("=" * 60)
    
    # Initialize database
    if not init_database():
        print("❌ Database initialization failed!")
        return
    
    # Verify database
    if not verify_database():
        print("❌ Database verification failed!")
        return
    
    # Run sample queries
    run_sample_queries()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization completed successfully!")
    print("✅ You can now run the CLI interface with: python hr_cli.py")
    print("✅ Or start the Flask app with: python app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
