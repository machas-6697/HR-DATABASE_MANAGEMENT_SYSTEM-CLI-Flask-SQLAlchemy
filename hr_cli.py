#!/usr/bin/env python3
"""
HR Database Management System - Command Line Interface
A comprehensive CLI for managing HR data, employees, departments, projects, and more.
"""

import click
import sqlite3
import os
from datetime import datetime, date, time
from tabulate import tabulate
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Database file path
DB_FILE = 'hr_database.db'

def get_db_connection():
    """Get database connection"""
    if not os.path.exists(DB_FILE):
        click.echo(f"{Fore.RED}❌ Database not found! Please run 'python init_db.py' first.{Style.RESET_ALL}")
        return None
    return sqlite3.connect(DB_FILE)

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

def display_table(data, headers, title=None):
    """Display data in a formatted table"""
    if title:
        click.echo(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
        click.echo("=" * len(title))
    
    if not data:
        click.echo(f"{Fore.YELLOW}No data found.{Style.RESET_ALL}")
        return
    
    table = tabulate(data, headers=headers, tablefmt="grid")
    click.echo(table)

# ============================================================================
# EMPLOYEE MANAGEMENT COMMANDS
# ============================================================================

@click.group()
def employee():
    """Employee management commands"""
    pass

@employee.command('list')
@click.option('--department', '-d', help='Filter by department name')
@click.option('--limit', '-l', default=50, help='Limit number of results')
def list_employees(department, limit):
    """List all employees with optional filters"""
    conn = get_db_connection()
    if not conn:
        return
    
    query = """
        SELECT 
            e.EmployeeID,
            e.FirstName,
            e.LastName,
            e.Email,
            jt.JobTitleName,
            d.DepartmentName,
            e.Salary,
            e.HireDate
        FROM Employees e
        JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID
        JOIN Departments d ON e.DepartmentID = d.DepartmentID
        WHERE 1=1
    """
    
    params = []
    if department:
        query += " AND d.DepartmentName LIKE ?"
        params.append(f"%{department}%")
    
    query += " ORDER BY e.LastName, e.FirstName LIMIT ?"
    params.append(limit)
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    employees = cursor.fetchall()
    
    headers = ['ID', 'First Name', 'Last Name', 'Email', 'Job Title', 'Department', 'Salary', 'Hire Date']
    
    # Format data
    formatted_data = []
    for emp in employees:
        formatted_data.append([
            emp[0],
            emp[1],
            emp[2],
            emp[3],
            emp[4],
            emp[5],
            format_currency(emp[6]),
            format_date(emp[7])
        ])
    
    display_table(formatted_data, headers, f"Employees ({len(employees)} found)")
    conn.close()

@employee.command('show')
@click.argument('employee_id', type=int)
def show_employee(employee_id):
    """Show detailed information about a specific employee"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get employee details
    cursor.execute("""
        SELECT 
            e.*,
            jt.JobTitleName,
            d.DepartmentName,
            m.FirstName || ' ' || m.LastName as ManagerName
        FROM Employees e
        JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID
        JOIN Departments d ON e.DepartmentID = d.DepartmentID
        LEFT JOIN Employees m ON e.ManagerID = m.EmployeeID
        WHERE e.EmployeeID = ?
    """, (employee_id,))
    
    emp = cursor.fetchone()
    if not emp:
        click.echo(f"{Fore.RED}❌ Employee with ID {employee_id} not found.{Style.RESET_ALL}")
        conn.close()
        return
    
    # Display employee details
    click.echo(f"\n{Fore.CYAN}Employee Details{Style.RESET_ALL}")
    click.echo("=" * 50)
    click.echo(f"ID: {emp[0]}")
    click.echo(f"Name: {emp[1]} {emp[2]}")
    click.echo(f"Gender: {emp[3]}")
    click.echo(f"Date of Birth: {format_date(emp[4])}")
    click.echo(f"Email: {emp[5]}")
    click.echo(f"Phone: {emp[6]}")
    click.echo(f"Hire Date: {format_date(emp[7])}")
    click.echo(f"Job Title: {emp[12]}")
    click.echo(f"Department: {emp[13]}")
    click.echo(f"Manager: {emp[14] or 'None'}")
    click.echo(f"Salary: {format_currency(emp[11])}")
    
    conn.close()

# ============================================================================
# DEPARTMENT MANAGEMENT COMMANDS
# ============================================================================

@click.group()
def department():
    """Department management commands"""
    pass

@department.command('list')
def list_departments():
    """List all departments"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            d.DepartmentID,
            d.DepartmentName,
            d.Location,
            e.FirstName || ' ' || e.LastName as HeadName,
            COUNT(emp.EmployeeID) as EmployeeCount
        FROM Departments d
        LEFT JOIN Employees e ON d.HeadID = e.EmployeeID
        LEFT JOIN Employees emp ON d.DepartmentID = emp.DepartmentID
        GROUP BY d.DepartmentID, d.DepartmentName, d.Location, e.FirstName, e.LastName
        ORDER BY d.DepartmentName
    """)
    
    departments = cursor.fetchall()
    headers = ['ID', 'Name', 'Location', 'Head', 'Employee Count']
    
    display_table(departments, headers, f"Departments ({len(departments)} found)")
    conn.close()

# ============================================================================
# PROJECT MANAGEMENT COMMANDS
# ============================================================================

@click.group()
def project():
    """Project management commands"""
    pass

@project.command('list')
def list_projects():
    """List all projects"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.ProjectID,
            p.ProjectName,
            d.DepartmentName,
            p.StartDate,
            p.EndDate,
            p.Budget,
            COUNT(ep.EmployeeID) as TeamSize
        FROM Projects p
        JOIN Departments d ON p.DepartmentID = d.DepartmentID
        LEFT JOIN EmployeeProjects ep ON p.ProjectID = ep.ProjectID
        GROUP BY p.ProjectID, p.ProjectName, d.DepartmentName, p.StartDate, p.EndDate, p.Budget
        ORDER BY p.StartDate
    """)
    
    projects = cursor.fetchall()
    headers = ['ID', 'Name', 'Department', 'Start Date', 'End Date', 'Budget', 'Team Size']
    
    # Format data
    formatted_data = []
    for proj in projects:
        formatted_data.append([
            proj[0],
            proj[1],
            proj[2],
            format_date(proj[3]),
            format_date(proj[4]),
            format_currency(proj[5]),
            proj[6]
        ])
    
    display_table(formatted_data, headers, f"Projects ({len(projects)} found)")
    conn.close()

# ============================================================================
# QUERY COMMANDS
# ============================================================================

@click.group()
def query():
    """Business intelligence and reporting queries"""
    pass

@query.command('top-salaries')
@click.option('--limit', '-l', default=3, help='Number of top employees per department')
def top_salaries_by_department(limit):
    """Find top N highest-paid employees per department"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    query = f"""
        WITH RankedEmployees AS (
            SELECT 
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                e.Salary,
                d.DepartmentID,
                d.DepartmentName,
                ROW_NUMBER() OVER (PARTITION BY d.DepartmentID ORDER BY e.Salary DESC) as SalaryRank
            FROM Employees e
            JOIN Departments d ON e.DepartmentID = d.DepartmentID
        )
        SELECT 
            DepartmentName,
            FirstName,
            LastName,
            Salary,
            SalaryRank
        FROM RankedEmployees
        WHERE SalaryRank <= {limit}
        ORDER BY DepartmentName, SalaryRank
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    headers = ['Department', 'First Name', 'Last Name', 'Salary', 'Rank']
    
    # Format data
    formatted_data = []
    for row in results:
        formatted_data.append([
            row[0],
            row[1],
            row[2],
            format_currency(row[3]),
            row[4]
        ])
    
    display_table(formatted_data, headers, f"Top {limit} Salaries by Department")
    conn.close()

@query.command('multi-projects')
@click.option('--min-projects', '-m', default=2, help='Minimum number of projects')
def employees_multiple_projects(min_projects):
    """Find employees working on multiple projects simultaneously"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    query = """
        SELECT 
            e.EmployeeID,
            e.FirstName,
            e.LastName,
            e.Email,
            COUNT(ep.ProjectID) as ProjectCount,
            GROUP_CONCAT(p.ProjectName, ', ') as Projects
        FROM Employees e
        JOIN EmployeeProjects ep ON e.EmployeeID = ep.EmployeeID
        JOIN Projects p ON ep.ProjectID = p.ProjectID
        GROUP BY e.EmployeeID, e.FirstName, e.LastName, e.Email
        HAVING COUNT(ep.ProjectID) > ?
        ORDER BY ProjectCount DESC
    """
    
    cursor.execute(query, (min_projects,))
    results = cursor.fetchall()
    
    headers = ['ID', 'Name', 'Email', 'Project Count', 'Projects']
    
    # Format data
    formatted_data = []
    for row in results:
        formatted_data.append([
            row[0],
            f"{row[1]} {row[2]}",
            row[3],
            row[4],
            row[5][:50] + "..." if len(row[5]) > 50 else row[5]
        ])
    
    display_table(formatted_data, headers, f"Employees with >{min_projects} Projects")
    conn.close()

@query.command('attendance-report')
@click.option('--month', '-m', default=datetime.now().month, help='Month (1-12)')
@click.option('--year', '-y', default=datetime.now().year, help='Year')
def monthly_attendance_report(month, year):
    """Generate monthly attendance report per department"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    query = """
        SELECT 
            d.DepartmentName,
            COUNT(CASE WHEN a.Status = 'Absent' THEN 1 END) as AbsentCount,
            COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) as PresentCount,
            COUNT(CASE WHEN a.Status = 'OnLeave' THEN 1 END) as OnLeaveCount,
            COUNT(CASE WHEN a.Status = 'WFH' THEN 1 END) as WFHCount,
            COUNT(*) as TotalDays,
            ROUND(COUNT(CASE WHEN a.Status = 'Absent' THEN 1 END) * 100.0 / COUNT(*), 2) as AbsenteeismRate
        FROM Attendance a
        JOIN Employees e ON a.EmployeeID = e.EmployeeID
        JOIN Departments d ON e.DepartmentID = d.DepartmentID
        WHERE strftime('%m', a.Date) = ? AND strftime('%Y', a.Date) = ?
        GROUP BY d.DepartmentID, d.DepartmentName
        ORDER BY AbsenteeismRate DESC
    """
    
    cursor.execute(query, (f"{month:02d}", str(year)))
    results = cursor.fetchall()
    
    headers = ['Department', 'Absent', 'Present', 'On Leave', 'WFH', 'Total Days', 'Absenteeism %']
    
    display_table(results, headers, f"Monthly Attendance Report - {month}/{year}")
    conn.close()

@query.command('payroll-cost')
@click.option('--year', '-y', default=datetime.now().year, help='Year')
def payroll_cost_by_department(year):
    """Show payroll cost per department per year"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    query = """
        SELECT 
            d.DepartmentName,
            COUNT(DISTINCT p.EmployeeID) as EmployeeCount,
            SUM(p.BasicSalary) as TotalBasicSalary,
            SUM(p.Allowances) as TotalAllowances,
            SUM(p.Deductions) as TotalDeductions,
            SUM(p.NetSalary) as TotalNetSalary,
            ROUND(AVG(p.NetSalary), 2) as AverageNetSalary
        FROM Payroll p
        JOIN Employees e ON p.EmployeeID = e.EmployeeID
        JOIN Departments d ON e.DepartmentID = d.DepartmentID
        WHERE p.Year = ?
        GROUP BY d.DepartmentID, d.DepartmentName
        ORDER BY TotalNetSalary DESC
    """
    
    cursor.execute(query, (year,))
    results = cursor.fetchall()
    
    headers = ['Department', 'Employees', 'Basic Salary', 'Allowances', 'Deductions', 'Net Salary', 'Avg Net Salary']
    
    # Format data
    formatted_data = []
    for row in results:
        formatted_data.append([
            row[0],
            row[1],
            format_currency(row[2]),
            format_currency(row[3]),
            format_currency(row[4]),
            format_currency(row[5]),
            format_currency(row[6])
        ])
    
    display_table(formatted_data, headers, f"Payroll Cost by Department - {year}")
    conn.close()

@query.command('run-all')
@click.option('--output-file', '-o', help='Save results to file')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def run_all_queries(output_file, verbose):
    """Execute all queries from queries.sql file"""
    conn = get_db_connection()
    if not conn:
        return
    
    if not os.path.exists('queries.sql'):
        click.echo(f"{Fore.RED}❌ queries.sql file not found!{Style.RESET_ALL}")
        return
    
    click.echo(f"{Fore.CYAN}🚀 Executing All Queries from queries.sql{Style.RESET_ALL}")
    click.echo("=" * 60)
    
    # Read queries.sql file
    try:
        with open('queries.sql', 'r') as f:
            content = f.read()
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Error reading queries.sql: {e}{Style.RESET_ALL}")
        return
    
    # Split content into individual queries
    queries = []
    current_query = ""
    in_comment = False
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('--'):
            continue
            
        # Check for multi-line comments
        if line.startswith('/*'):
            in_comment = True
            continue
        if line.endswith('*/'):
            in_comment = False
            continue
        if in_comment:
            continue
            
        current_query += line + " "
        
        # If line ends with semicolon, it's a complete query
        if line.endswith(';'):
            queries.append(current_query.strip())
            current_query = ""
    
    if current_query.strip():  # Add any remaining query
        queries.append(current_query.strip())
    
    click.echo(f"📊 Found {len(queries)} queries to execute")
    click.echo()
    
    # Execute each query
    all_results = []
    cursor = conn.cursor()
    
    for i, query in enumerate(queries, 1):
        if not query.strip():
            continue
            
        try:
            click.echo(f"{Fore.YELLOW}Query {i}:{Style.RESET_ALL}")
            if verbose:
                click.echo(f"   {query[:100]}{'...' if len(query) > 100 else ''}")
            
            # Execute query
            cursor.execute(query)
            
            # Try to fetch results
            try:
                results = cursor.fetchall()
                if results:
                    # Get column names
                    column_names = [description[0] for description in cursor.description]
                    
                    if verbose:
                        click.echo(f"   ✅ Results: {len(results)} rows")
                        # Show first few rows
                        if len(results) <= 5:
                            table = tabulate(results, headers=column_names, tablefmt="grid")
                            click.echo(f"   {table}")
                        else:
                            table = tabulate(results[:3], headers=column_names, tablefmt="grid")
                            click.echo(f"   {table}")
                            click.echo(f"   ... and {len(results) - 3} more rows")
                    else:
                        click.echo(f"   ✅ {len(results)} rows returned")
                    
                    all_results.append({
                        'query_num': i,
                        'query': query[:100] + '...' if len(query) > 100 else query,
                        'rows': len(results),
                        'columns': column_names
                    })
                else:
                    click.echo(f"   ✅ Query executed successfully (no results)")
                    all_results.append({
                        'query_num': i,
                        'query': query[:100] + '...' if len(query) > 100 else query,
                        'rows': 0,
                        'columns': []
                    })
                    
            except sqlite3.OperationalError:
                # Query executed but no results to fetch (e.g., INSERT, UPDATE, DELETE)
                click.echo(f"   ✅ Query executed successfully")
                all_results.append({
                    'query_num': i,
                    'query': query[:100] + '...' if len(query) > 100 else query,
                    'rows': 'N/A',
                    'columns': []
                })
                
        except sqlite3.OperationalError as e:
            click.echo(f"   ❌ Error: {e}")
            all_results.append({
                'query_num': i,
                'query': query[:100] + '...' if len(query) > 100 else query,
                'rows': 'ERROR',
                'columns': [],
                'error': str(e)
            })
        except Exception as e:
            click.echo(f"   ❌ Unexpected error: {e}")
            all_results.append({
                'query_num': i,
                'query': query[:100] + '...' if len(query) > 100 else query,
                'rows': 'ERROR',
                'columns': [],
                'error': str(e)
            })
        
        click.echo()
    
    # Summary
    click.echo(f"{Fore.GREEN}📋 Execution Summary:{Style.RESET_ALL}")
    click.echo("=" * 40)
    
    successful = sum(1 for r in all_results if r.get('rows') != 'ERROR')
    failed = sum(1 for r in all_results if r.get('rows') == 'ERROR')
    
    click.echo(f"✅ Successful: {successful}")
    click.echo(f"❌ Failed: {failed}")
    click.echo(f"📊 Total: {len(queries)}")
    
    # Save results to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write("Query Execution Results\n")
                f.write("=" * 30 + "\n\n")
                
                for result in all_results:
                    f.write(f"Query {result['query_num']}:\n")
                    f.write(f"SQL: {result['query']}\n")
                    f.write(f"Status: {'SUCCESS' if result.get('rows') != 'ERROR' else 'FAILED'}\n")
                    if result.get('rows') != 'ERROR':
                        f.write(f"Results: {result['rows']} rows\n")
                        if result.get('columns'):
                            f.write(f"Columns: {', '.join(result['columns'])}\n")
                    else:
                        f.write(f"Error: {result.get('error', 'Unknown error')}\n")
                    f.write("-" * 40 + "\n\n")
            
            click.echo(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            click.echo(f"{Fore.RED}❌ Error saving results: {e}{Style.RESET_ALL}")
    
    conn.close()

@query.command('dashboard')
def dashboard():
    """Show comprehensive system dashboard"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get key metrics
    metrics = []
    
    # Total employees
    cursor.execute("SELECT COUNT(*) FROM Employees")
    emp_count = cursor.fetchone()[0]
    metrics.append(['Total Employees', emp_count, ''])
    
    # Total departments
    cursor.execute("SELECT COUNT(*) FROM Departments")
    dept_count = cursor.fetchone()[0]
    metrics.append(['Total Departments', dept_count, ''])
    
    # Active projects
    cursor.execute("""
        SELECT COUNT(*) FROM Projects 
        WHERE date('now') BETWEEN StartDate AND EndDate
    """)
    active_projects = cursor.fetchone()[0]
    metrics.append(['Active Projects', active_projects, ''])
    
    # Average salary
    cursor.execute("SELECT ROUND(AVG(Salary), 2) FROM Employees")
    avg_salary = cursor.fetchone()[0]
    metrics.append(['Average Salary', format_currency(avg_salary), ''])
    
    # Total payroll cost Q1 2024
    cursor.execute("""
        SELECT ROUND(SUM(NetSalary), 2) FROM Payroll 
        WHERE Year = 2024 AND Month IN (1, 2, 3)
    """)
    q1_payroll = cursor.fetchone()[0] or 0
    metrics.append(['Q1 2024 Payroll Cost', format_currency(q1_payroll), ''])
    
    # Average performance rating
    cursor.execute("""
        SELECT ROUND(AVG(Rating), 2) FROM PerformanceReviews 
        WHERE ReviewDate >= date('now', '-1 year')
    """)
    avg_rating = cursor.fetchone()[0] or 0
    metrics.append(['Average Performance Rating', avg_rating, ''])
    
    # Pending leave requests
    cursor.execute("SELECT COUNT(*) FROM LeaveRequests WHERE Status = 'Pending'")
    pending_leaves = cursor.fetchone()[0]
    metrics.append(['Pending Leave Requests', pending_leaves, ''])
    
    headers = ['Metric', 'Value', 'Detail']
    display_table(metrics, headers, "System Dashboard")
    
    conn.close()

# ============================================================================
# MAIN CLI GROUP
# ============================================================================

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """HR Database Management System - CLI Interface
    
    A comprehensive command-line interface for managing HR data,
    employees, departments, projects, and generating business reports.
    
    Use --help with any command to see detailed options.
    """
    pass

# Add all command groups to main CLI
cli.add_command(employee)
cli.add_command(department)
cli.add_command(project)
cli.add_command(query)

# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@cli.command('status')
def system_status():
    """Show system status and database information"""
    click.echo(f"{Fore.CYAN}HR Database Management System - Status{Style.RESET_ALL}")
    click.echo("=" * 50)
    
    # Check database file
    if os.path.exists(DB_FILE):
        db_size = os.path.getsize(DB_FILE)
        click.echo(f"✅ Database: {DB_FILE}")
        click.echo(f"   Size: {db_size:,} bytes")
        
        # Check database content
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Count records in each table
            tables = ['JobTitles', 'Departments', 'Employees', 'Projects', 
                     'EmployeeProjects', 'Attendance', 'LeaveRequests', 
                     'PerformanceReviews', 'Payroll']
            
            click.echo(f"\n📊 Database Contents:")
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    click.echo(f"   {table}: {count:,} records")
                except:
                    click.echo(f"   {table}: Error")
            
            conn.close()
    else:
        click.echo(f"❌ Database: {DB_FILE} not found")
        click.echo("   Run 'python init_db.py' to initialize the database")
    
    click.echo(f"\n🔧 Available Commands:")
    click.echo("   employee list    - List all employees")
    click.echo("   employee show    - Show employee details")
    click.echo("   department list  - List all departments")
    click.echo("   project list     - List all projects")
    click.echo("   query dashboard  - Show system dashboard")
    click.echo("   query top-salaries - Top salaries by department")
    click.echo("   query multi-projects - Employees on multiple projects")
    click.echo("   query attendance-report - Monthly attendance report")
    click.echo("   query payroll-cost - Payroll cost by department")
    click.echo("   query run-all     - Execute all queries from queries.sql")

@cli.command('init')
def initialize_system():
    """Initialize the database system"""
    click.echo(f"{Fore.YELLOW}Initializing HR Database Management System...{Style.RESET_ALL}")
    
    if os.path.exists('init_db.py'):
        import subprocess
        try:
            result = subprocess.run(['python', 'init_db.py'], capture_output=True, text=True)
            if result.returncode == 0:
                click.echo(f"{Fore.GREEN}✅ System initialized successfully!{Style.RESET_ALL}")
            else:
                click.echo(f"{Fore.RED}❌ Initialization failed:{Style.RESET_ALL}")
                click.echo(result.stderr)
        except Exception as e:
            click.echo(f"{Fore.RED}❌ Error running init script: {e}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}❌ init_db.py not found!{Style.RESET_ALL}")

if __name__ == '__main__':
    cli()
