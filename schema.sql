-- HR Database Management System - Complete Schema
-- This file contains the DDL (Data Definition Language) for all tables

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS Payroll;
DROP TABLE IF EXISTS PerformanceReviews;
DROP TABLE IF EXISTS LeaveRequests;
DROP TABLE IF EXISTS Attendance;
DROP TABLE IF EXISTS EmployeeProjects;
DROP TABLE IF EXISTS Projects;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS JobTitles;
DROP TABLE IF EXISTS Departments;

-- Table 1: Departments
CREATE TABLE Departments (
    DepartmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    DepartmentName VARCHAR(100) NOT NULL UNIQUE,
    Location VARCHAR(100) NOT NULL,
    HeadID INTEGER,
    FOREIGN KEY (HeadID) REFERENCES Employees(EmployeeID)
);

-- Table 2: JobTitles
CREATE TABLE JobTitles (
    JobTitleID INTEGER PRIMARY KEY AUTOINCREMENT,
    JobTitleName VARCHAR(100) NOT NULL UNIQUE,
    MinSalary DECIMAL(10,2) NOT NULL,
    MaxSalary DECIMAL(10,2) NOT NULL
);

-- Table 3: Employees
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Gender CHAR(1) CHECK (Gender IN ('M', 'F', 'O')),
    DOB DATE NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Phone VARCHAR(20),
    HireDate DATE NOT NULL,
    JobTitleID INTEGER NOT NULL,
    DepartmentID INTEGER NOT NULL,
    ManagerID INTEGER,
    Salary DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (JobTitleID) REFERENCES JobTitles(JobTitleID),
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID),
    FOREIGN KEY (ManagerID) REFERENCES Employees(EmployeeID)
);

-- Table 4: Projects
CREATE TABLE Projects (
    ProjectID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProjectName VARCHAR(200) NOT NULL,
    DepartmentID INTEGER NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,
    Budget DECIMAL(12,2),
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

-- Table 5: EmployeeProjects (Bridge Table)
CREATE TABLE EmployeeProjects (
    EmployeeID INTEGER NOT NULL,
    ProjectID INTEGER NOT NULL,
    Role VARCHAR(100) NOT NULL,
    AllocationPercent DECIMAL(5,2) DEFAULT 100.00,
    PRIMARY KEY (EmployeeID, ProjectID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
);

-- Table 6: Attendance
CREATE TABLE Attendance (
    AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    EmployeeID INTEGER NOT NULL,
    Date DATE NOT NULL,
    CheckInTime TIME,
    CheckOutTime TIME,
    Status VARCHAR(20) CHECK (Status IN ('Present', 'Absent', 'OnLeave', 'WFH')),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Table 7: LeaveRequests
CREATE TABLE LeaveRequests (
    LeaveID INTEGER PRIMARY KEY AUTOINCREMENT,
    EmployeeID INTEGER NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    LeaveType VARCHAR(20) CHECK (LeaveType IN ('Sick', 'Casual', 'Vacation')),
    Status VARCHAR(20) CHECK (Status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
    ApprovedBy INTEGER,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    FOREIGN KEY (ApprovedBy) REFERENCES Employees(EmployeeID)
);

-- Table 8: PerformanceReviews
CREATE TABLE PerformanceReviews (
    ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
    EmployeeID INTEGER NOT NULL,
    ReviewerID INTEGER NOT NULL,
    ReviewDate DATE NOT NULL,
    Rating INTEGER CHECK (Rating >= 1 AND Rating <= 5),
    Comments TEXT,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    FOREIGN KEY (ReviewerID) REFERENCES Employees(EmployeeID)
);

-- Table 9: Payroll
CREATE TABLE Payroll (
    PayrollID INTEGER PRIMARY KEY AUTOINCREMENT,
    EmployeeID INTEGER NOT NULL,
    Month INTEGER CHECK (Month >= 1 AND Month <= 12),
    Year INTEGER CHECK (Year >= 2000),
    BasicSalary DECIMAL(10,2) NOT NULL,
    Allowances DECIMAL(10,2) DEFAULT 0.00,
    Deductions DECIMAL(10,2) DEFAULT 0.00,
    NetSalary DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Create indexes for better performance
CREATE INDEX idx_employees_department ON Employees(DepartmentID);
CREATE INDEX idx_employees_manager ON Employees(ManagerID);
CREATE INDEX idx_employees_jobtitle ON Employees(JobTitleID);
CREATE INDEX idx_attendance_employee_date ON Attendance(EmployeeID, Date);
CREATE INDEX idx_leave_employee ON LeaveRequests(EmployeeID);
CREATE INDEX idx_payroll_employee_month_year ON Payroll(EmployeeID, Month, Year);
CREATE INDEX idx_employee_projects_employee ON EmployeeProjects(EmployeeID);
CREATE INDEX idx_employee_projects_project ON EmployeeProjects(ProjectID);

-- Add constraints to ensure data integrity
-- Ensure salary is within job title range
CREATE TRIGGER check_salary_range
BEFORE INSERT ON Employees
FOR EACH ROW
BEGIN
    SELECT CASE 
        WHEN NEW.Salary < (SELECT MinSalary FROM JobTitles WHERE JobTitleID = NEW.JobTitleID)
        OR NEW.Salary > (SELECT MaxSalary FROM JobTitles WHERE JobTitleID = NEW.JobTitleID)
        THEN RAISE(ABORT, 'Salary must be within job title range')
    END;
END;

-- Ensure allocation percentage is valid
CREATE TRIGGER check_allocation_percent
BEFORE INSERT ON EmployeeProjects
FOR EACH ROW
BEGIN
    SELECT CASE 
        WHEN NEW.AllocationPercent < 0 OR NEW.AllocationPercent > 100
        THEN RAISE(ABORT, 'Allocation percentage must be between 0 and 100')
    END;
END;
