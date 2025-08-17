# HR Database Management System - Setup Guide

This guide will walk you through setting up and running the HR Database Management System.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Install Dependencies

First, install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- Flask 2.3.3 - Web framework
- Flask-SQLAlchemy 3.0.5 - Database ORM
- Click 8.1.7 - CLI framework
- Tabulate 0.9.0 - Table formatting
- Python-dotenv 1.0.0 - Environment variables
- Colorama 0.4.6 - Cross-platform colored output

### 2. Initialize the Database

Run the database initialization script to create the database and load sample data:

```bash
python init_db.py
```

This script will:
- Create the SQLite database (`hr_database.db`)
- Create all 9 tables with proper relationships
- Load sample data (10+ records per table)
- Verify the database structure
- Run sample queries to test functionality

**Expected Output:**
```
============================================================
HR Database Management System - Database Initialization
============================================================
Creating database tables...
✓ Database schema created successfully.
Loading sample data...
✓ Sample data loaded successfully.
✓ Database initialization completed successfully!

Verifying database structure...
✓ JobTitles table exists
✓ Departments table exists
✓ Employees table exists
✓ Projects table exists
✓ EmployeeProjects table exists
✓ Attendance table exists
✓ LeaveRequests table exists
✓ PerformanceReviews table exists
✓ Payroll table exists

Checking record counts...
✓ JobTitles: 25 records
✓ Departments: 15 records
✓ Employees: 25 records
✓ Projects: 15 records
✓ EmployeeProjects: 35 records
✓ Attendance: 200 records
✓ LeaveRequests: 15 records
✓ PerformanceReviews: 19 records
✓ Payroll: 75 records
```

### 3. Test the System

Run the test script to verify everything is working:

```bash
python test_system.py
```

**Expected Output:**
```
============================================================
HR Database Management System - System Test
============================================================
Testing database connection...
✅ Database connection successful

Testing basic queries...
✅ Employees count: 25
✅ Departments count: 15
✅ Projects count: 15

Testing complex query (top salaries by department)...
✅ Complex query successful, returned 15 rows

Sample results:
  1. Executive - John Smith ($200,000.00) - Rank 1
  2. Engineering - Emily Davis ($140,000.00) - Rank 1
  3. Sales - David Wilson ($130,000.00) - Rank 1

Testing CLI command availability...
✅ CLI help command works
✅ CLI status command works

============================================================
✅ All tests passed! System is working correctly.
✅ You can now use the CLI interface:
   python hr_cli.py --help
   python hr_cli.py status
   python hr_cli.py employee list
   python hr_cli.py query dashboard
============================================================
```

## Usage

### CLI Interface

The system provides a comprehensive command-line interface:

#### Basic Commands

```bash
# Show system status
python hr_cli.py status

# Show help
python hr_cli.py --help

# Initialize system (if needed)
python hr_cli.py init
```

#### Employee Management

```bash
# List all employees
python hr_cli.py employee list

# List employees in a specific department
python hr_cli.py employee list --department "Engineering"

# Show detailed employee information
python hr_cli.py employee show 1
```

#### Department Management

```bash
# List all departments
python hr_cli.py department list

# Show department details
python hr_cli.py department show 1
```

#### Project Management

```bash
# List all projects
python hr_cli.py project list
```

#### Business Intelligence Queries

```bash
# Show system dashboard
python hr_cli.py query dashboard

# Top 3 highest-paid employees per department
python hr_cli.py query top-salaries --limit 3

# Employees working on multiple projects
python hr_cli.py query multi-projects --min-projects 2

# Monthly attendance report
python hr_cli.py query attendance-report --month 3 --year 2024

# Payroll cost by department
python hr_cli.py query payroll-cost --year 2024
```

### Web Interface (Optional)

You can also run the Flask web application:

```bash
python app.py
```

Then open your browser to `http://localhost:5000` to see the system status page.

## Database Schema

The system includes 9 core tables:

1. **Employees** - Employee information and hierarchy
2. **Departments** - Department structure and locations
3. **JobTitles** - Job positions and salary ranges
4. **Projects** - Project details and budgets
5. **EmployeeProjects** - Employee-project assignments
6. **Attendance** - Daily attendance tracking
7. **LeaveRequests** - Leave management
8. **PerformanceReviews** - Employee performance evaluation
9. **Payroll** - Salary and compensation records

## Sample Data

The system comes with comprehensive sample data:

- **25 Job Titles** - From CEO to Junior Developer
- **15 Departments** - Executive, Engineering, Sales, Marketing, etc.
- **25 Employees** - Complete with realistic data
- **15 Projects** - Various types and budgets
- **35 Employee-Project Assignments** - Multiple roles and allocations
- **200 Attendance Records** - March 2024 data
- **15 Leave Requests** - Various types and statuses
- **19 Performance Reviews** - Ratings and comments
- **75 Payroll Records** - Q1 2024 data

## Business Intelligence Queries

The system includes 20+ real-world queries:

### Core Queries (as requested)
1. **Top 3 highest-paid employees per department**
2. **Average salary hike after promotions**
3. **Employees working on multiple projects simultaneously**
4. **Monthly absenteeism report per department**
5. **Payroll cost per department per year**

### Additional Queries
6. Employee turnover analysis
7. Project budget utilization
8. Performance review analysis
9. Leave request analysis
10. Salary distribution analysis
11. Employee hierarchy structure
12. Department head analysis
13. Project timeline analysis
14. Employee skill matrix
15. Financial analysis
16. Attendance patterns
17. Department cost efficiency
18. Employee retention analysis
19. Project success metrics
20. Comprehensive dashboard

## Troubleshooting

### Common Issues

1. **Database not found error**
   ```
   ❌ Database not found! Please run 'python init_db.py' first.
   ```
   **Solution:** Run `python init_db.py` to create the database.

2. **Import errors**
   ```
   ModuleNotFoundError: No module named 'flask'
   ```
   **Solution:** Install dependencies with `pip install -r requirements.txt`

3. **Permission errors**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution:** Check file permissions or run with appropriate privileges.

4. **SQLite errors**
   ```
   sqlite3.OperationalError: no such table
   ```
   **Solution:** The database wasn't initialized properly. Run `python init_db.py`.

### Verification Steps

If you encounter issues, follow these verification steps:

1. **Check Python version:**
   ```bash
   python --version
   # Should be 3.7 or higher
   ```

2. **Check dependencies:**
   ```bash
   pip list | grep -E "(Flask|Click|tabulate|colorama)"
   ```

3. **Check database file:**
   ```bash
   ls -la hr_database.db
   # Should exist and be readable
   ```

4. **Test database connection:**
   ```bash
   python test_system.py
   ```

## File Structure

```
HR-database-management-CLI/
├── app.py                 # Flask application
├── hr_cli.py             # CLI interface
├── init_db.py            # Database initialization
├── test_system.py        # System testing
├── schema.sql            # Database schema (DDL)
├── data.sql              # Sample data
├── queries.sql           # Business intelligence queries
├── requirements.txt      # Python dependencies
├── README.md             # Project overview
├── SETUP.md              # This setup guide
└── hr_database.db        # SQLite database (created after init)
```

## Support

If you encounter any issues:

1. Check this setup guide
2. Run the test script: `python test_system.py`
3. Check the error messages for specific issues
4. Verify all dependencies are installed
5. Ensure the database was initialized properly

## Next Steps

After successful setup:

1. **Explore the CLI:** Try different commands to understand the system
2. **Run queries:** Execute business intelligence queries to see the data
3. **Customize:** Modify the sample data or add new records
4. **Extend:** Add new features or modify existing functionality

The system is designed to be easily extensible and customizable for your specific HR needs.
