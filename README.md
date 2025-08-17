# HR Database Management System

A comprehensive HR database management system built with Python Flask and SQLite, featuring a powerful CLI interface for managing employee data, departments, projects, and more.

## Features

- **Complete Database Schema**: 9 core tables with proper relationships
- **CLI Interface**: Easy-to-use command-line interface
- **Employee Management**: Full CRUD operations for employees
- **Department Management**: Handle departments and reporting structures
- **Project Management**: Track projects and employee allocations
- **Attendance & Leave**: Monitor attendance and leave requests
- **Performance Reviews**: Employee performance tracking
- **Payroll Management**: Salary and compensation tracking
- **Advanced Queries**: 20+ real-world business queries

## Database Schema

### Core Tables
1. **Employees** - Employee information and hierarchy
2. **Departments** - Department structure and locations
3. **JobTitles** - Job positions and salary ranges
4. **Projects** - Project details and budgets
5. **EmployeeProjects** - Employee-project assignments
6. **Attendance** - Daily attendance tracking
7. **LeaveRequests** - Leave management
8. **PerformanceReviews** - Employee performance evaluation
9. **Payroll** - Salary and compensation records

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize database: `python init_db.py`
4. Run the CLI: `python hr_cli.py`

## Usage

```bash
# Initialize the database
python init_db.py

# Run the CLI
python hr_cli.py

# Available commands
python hr_cli.py --help
python hr_cli.py employee --help
python hr_cli.py department --help
python hr_cli.py project --help
python hr_cli.py query --help
```

## Sample Queries

The system includes 20+ real-world queries such as:
- Top 3 highest-paid employees per department
- Average salary hike after promotions
- Employees working on multiple projects
- Monthly absenteeism reports
- Payroll cost analysis

## Database Files

- `schema.sql` - Complete database schema (DDL)
- `data.sql` - Sample data with 10+ records per table
- `queries.sql` - 20+ business intelligence queries
