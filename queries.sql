-- HR Database Management System - Business Intelligence Queries
-- This file contains 20+ real-world queries for HR analytics and reporting

-- ============================================================================
-- QUERY 1: Find top 3 highest-paid employees per department
-- ============================================================================
SELECT 
    d.DepartmentName,
    e.FirstName,
    e.LastName,
    e.Salary,
    ROW_NUMBER() OVER (PARTITION BY d.DepartmentID ORDER BY e.Salary DESC) as SalaryRank
FROM Employees e
JOIN Departments d ON e.DepartmentID = d.DepartmentID
WHERE ROW_NUMBER() OVER (PARTITION BY d.DepartmentID ORDER BY e.Salary DESC) <= 3
ORDER BY d.DepartmentName, e.Salary DESC;

-- Alternative approach using CTE
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
WHERE SalaryRank <= 3
ORDER BY DepartmentName, SalaryRank;

-- ============================================================================
-- QUERY 2: Calculate average salary hike after promotions
-- ============================================================================
-- This query assumes we have historical salary data or can track salary changes
-- For demonstration, we'll show salary distribution by job title and experience

SELECT 
    jt.JobTitleName,
    COUNT(e.EmployeeID) as EmployeeCount,
    AVG(e.Salary) as AverageSalary,
    MIN(e.Salary) as MinSalary,
    MAX(e.Salary) as MaxSalary,
    ROUND((MAX(e.Salary) - MIN(e.Salary)) / MIN(e.Salary) * 100, 2) as SalaryRangePercentage
FROM Employees e
JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID
GROUP BY jt.JobTitleID, jt.JobTitleName
ORDER BY AverageSalary DESC;

-- ============================================================================
-- QUERY 3: Get employees who worked on more than 2 projects simultaneously
-- ============================================================================
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
HAVING COUNT(ep.ProjectID) > 2
ORDER BY ProjectCount DESC;

-- ============================================================================
-- QUERY 4: Monthly absenteeism report per department
-- ============================================================================
SELECT 
    d.DepartmentName,
    strftime('%Y-%m', a.Date) as Month,
    COUNT(CASE WHEN a.Status = 'Absent' THEN 1 END) as AbsentCount,
    COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) as PresentCount,
    COUNT(CASE WHEN a.Status = 'OnLeave' THEN 1 END) as OnLeaveCount,
    COUNT(CASE WHEN a.Status = 'WFH' THEN 1 END) as WFHCount,
    COUNT(*) as TotalDays,
    ROUND(COUNT(CASE WHEN a.Status = 'Absent' THEN 1 END) * 100.0 / COUNT(*), 2) as AbsenteeismRate
FROM Attendance a
JOIN Employees e ON a.EmployeeID = e.EmployeeID
JOIN Departments d ON e.DepartmentID = d.DepartmentID
WHERE a.Date >= '2024-01-01' AND a.Date <= '2024-12-31'
GROUP BY d.DepartmentID, d.DepartmentName, strftime('%Y-%m', a.Date)
ORDER BY d.DepartmentName, Month;

-- ============================================================================
-- QUERY 5: Payroll cost per department per year
-- ============================================================================
SELECT 
    d.DepartmentName,
    p.Year,
    COUNT(DISTINCT p.EmployeeID) as EmployeeCount,
    SUM(p.BasicSalary) as TotalBasicSalary,
    SUM(p.Allowances) as TotalAllowances,
    SUM(p.Deductions) as TotalDeductions,
    SUM(p.NetSalary) as TotalNetSalary,
    ROUND(AVG(p.NetSalary), 2) as AverageNetSalary
FROM Payroll p
JOIN Employees e ON p.EmployeeID = e.EmployeeID
JOIN Departments d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentID, d.DepartmentName, p.Year
ORDER BY d.DepartmentName, p.Year;

-- ============================================================================
-- QUERY 6: Employee turnover analysis by department
-- ============================================================================
SELECT 
    d.DepartmentName,
    COUNT(e.EmployeeID) as CurrentEmployees,
    COUNT(CASE WHEN e.HireDate >= date('now', '-1 year') THEN 1 END) as HiredLastYear,
    COUNT(CASE WHEN e.HireDate < date('now', '-5 years') THEN 1 END) as LongTermEmployees,
    ROUND(AVG(julianday('now') - julianday(e.HireDate)) / 365.25, 2) as AverageTenureYears
FROM Employees e
JOIN Departments d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentID, d.DepartmentName
ORDER BY CurrentEmployees DESC;

-- ============================================================================
-- QUERY 7: Project budget utilization and employee allocation
-- ============================================================================
SELECT 
    p.ProjectName,
    d.DepartmentName,
    p.Budget,
    COUNT(ep.EmployeeID) as AssignedEmployees,
    SUM(ep.AllocationPercent) as TotalAllocation,
    ROUND(p.Budget / COUNT(ep.EmployeeID), 2) as BudgetPerEmployee,
    p.StartDate,
    p.EndDate,
    CASE 
        WHEN date('now') < p.StartDate THEN 'Not Started'
        WHEN date('now') BETWEEN p.StartDate AND p.EndDate THEN 'In Progress'
        ELSE 'Completed'
    END as ProjectStatus
FROM Projects p
JOIN Departments d ON p.DepartmentID = d.DepartmentID
LEFT JOIN EmployeeProjects ep ON p.ProjectID = ep.ProjectID
GROUP BY p.ProjectID, p.ProjectName, d.DepartmentName, p.Budget, p.StartDate, p.EndDate
ORDER BY p.StartDate;

-- ============================================================================
-- QUERY 8: Performance review analysis by department and rating
-- ============================================================================
SELECT 
    d.DepartmentName,
    pr.Rating,
    COUNT(*) as ReviewCount,
    ROUND(AVG(pr.Rating), 2) as AverageRating,
    COUNT(CASE WHEN pr.Rating >= 4 THEN 1 END) as HighPerformers,
    COUNT(CASE WHEN pr.Rating <= 2 THEN 1 END) as LowPerformers,
    ROUND(COUNT(CASE WHEN pr.Rating >= 4 THEN 1 END) * 100.0 / COUNT(*), 2) as HighPerformerPercentage
FROM PerformanceReviews pr
JOIN Employees e ON pr.EmployeeID = e.EmployeeID
JOIN Departments d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentID, d.DepartmentName, pr.Rating
ORDER BY d.DepartmentName, pr.Rating DESC;

-- ============================================================================
-- QUERY 9: Leave request analysis by type and status
-- ============================================================================
SELECT 
    lr.LeaveType,
    lr.Status,
    COUNT(*) as RequestCount,
    ROUND(AVG(julianday(lr.EndDate) - julianday(lr.StartDate) + 1), 1) as AverageDays,
    COUNT(CASE WHEN lr.Status = 'Approved' THEN 1 END) as ApprovedCount,
    COUNT(CASE WHEN lr.Status = 'Rejected' THEN 1 END) as RejectedCount,
    COUNT(CASE WHEN lr.Status = 'Pending' THEN 1 END) as PendingCount
FROM LeaveRequests lr
GROUP BY lr.LeaveType, lr.Status
ORDER BY lr.LeaveType, lr.Status;

-- ============================================================================
-- QUERY 10: Salary distribution analysis by job title and experience
-- ============================================================================
SELECT 
    jt.JobTitleName,
    jt.MinSalary,
    jt.MaxSalary,
    COUNT(e.EmployeeID) as EmployeeCount,
    ROUND(AVG(e.Salary), 2) as AverageSalary,
    ROUND(MIN(e.Salary), 2) as MinActualSalary,
    ROUND(MAX(e.Salary), 2) as MaxActualSalary,
    ROUND(AVG(e.Salary) - jt.MinSalary, 2) as AvgAboveMin,
    ROUND(jt.MaxSalary - AVG(e.Salary), 2) as AvgBelowMax,
    ROUND((AVG(e.Salary) - jt.MinSalary) / (jt.MaxSalary - jt.MinSalary) * 100, 2) as SalaryPositionPercentage
FROM JobTitles jt
LEFT JOIN Employees e ON jt.JobTitleID = e.JobTitleID
GROUP BY jt.JobTitleID, jt.JobTitleName, jt.MinSalary, jt.MaxSalary
ORDER BY jt.MinSalary DESC;

-- ============================================================================
-- QUERY 11: Employee hierarchy and reporting structure
-- ============================================================================
WITH RECURSIVE EmployeeHierarchy AS (
    -- Base case: employees with no manager (top level)
    SELECT 
        EmployeeID, 
        FirstName, 
        LastName, 
        JobTitleID, 
        DepartmentID, 
        ManagerID, 
        0 as Level,
        FirstName || ' ' || LastName as HierarchyPath
    FROM Employees 
    WHERE ManagerID IS NULL
    
    UNION ALL
    
    -- Recursive case: employees with managers
    SELECT 
        e.EmployeeID, 
        e.FirstName, 
        e.LastName, 
        e.JobTitleID, 
        e.DepartmentID, 
        e.ManagerID, 
        eh.Level + 1,
        eh.HierarchyPath || ' > ' || e.FirstName || ' ' || e.LastName
    FROM Employees e
    JOIN EmployeeHierarchy eh ON e.ManagerID = eh.EmployeeID
)
SELECT 
    eh.Level,
    eh.HierarchyPath,
    jt.JobTitleName,
    d.DepartmentName,
    eh.FirstName,
    eh.LastName
FROM EmployeeHierarchy eh
JOIN JobTitles jt ON eh.JobTitleID = jt.JobTitleID
JOIN Departments d ON eh.DepartmentID = d.DepartmentID
ORDER BY eh.Level, eh.HierarchyPath;

-- ============================================================================
-- QUERY 12: Department head analysis and their team sizes
-- ============================================================================
SELECT 
    d.DepartmentName,
    d.Location,
    CONCAT(e.FirstName, ' ', e.LastName) as DepartmentHead,
    jt.JobTitleName as HeadJobTitle,
    e.Salary as HeadSalary,
    COUNT(emp.EmployeeID) as TeamSize,
    ROUND(AVG(emp.Salary), 2) as TeamAverageSalary,
    ROUND(e.Salary / AVG(emp.Salary), 2) as HeadToTeamSalaryRatio
FROM Departments d
JOIN Employees e ON d.HeadID = e.EmployeeID
JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID
LEFT JOIN Employees emp ON d.DepartmentID = emp.DepartmentID
GROUP BY d.DepartmentID, d.DepartmentName, d.Location, e.EmployeeID, e.FirstName, e.LastName, jt.JobTitleName, e.Salary
ORDER BY TeamSize DESC;

-- ============================================================================
-- QUERY 13: Project timeline analysis and resource allocation
-- ============================================================================
SELECT 
    p.ProjectName,
    d.DepartmentName,
    p.StartDate,
    p.EndDate,
    julianday(p.EndDate) - julianday(p.StartDate) + 1 as ProjectDurationDays,
    p.Budget,
    COUNT(ep.EmployeeID) as AssignedEmployees,
    SUM(ep.AllocationPercent) as TotalAllocation,
    ROUND(p.Budget / (julianday(p.EndDate) - julianday(p.StartDate) + 1), 2) as DailyBudget,
    ROUND(p.Budget / COUNT(ep.EmployeeID), 2) as BudgetPerEmployee,
    CASE 
        WHEN date('now') < p.StartDate THEN 'Not Started'
        WHEN date('now') BETWEEN p.StartDate AND p.EndDate THEN 'In Progress'
        ELSE 'Completed'
    END as ProjectStatus
FROM Projects p
JOIN Departments d ON p.DepartmentID = d.DepartmentID
LEFT JOIN EmployeeProjects ep ON p.ProjectID = ep.ProjectID
GROUP BY p.ProjectID, p.ProjectName, d.DepartmentName, p.StartDate, p.EndDate, p.Budget
ORDER BY p.StartDate;

-- ============================================================================
-- QUERY 14: Employee skill matrix based on project roles
-- ============================================================================
SELECT 
    e.FirstName,
    e.LastName,
    e.Email,
    d.DepartmentName,
    jt.JobTitleName,
    COUNT(DISTINCT ep.ProjectID) as TotalProjects,
    GROUP_CONCAT(DISTINCT ep.Role, ', ') as Roles,
    GROUP_CONCAT(DISTINCT p.ProjectName, ' | ') as Projects,
    ROUND(AVG(ep.AllocationPercent), 2) as AverageAllocation,
    SUM(ep.AllocationPercent) as TotalAllocation
FROM Employees e
JOIN Departments d ON e.DepartmentID = d.DepartmentID
JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID
LEFT JOIN EmployeeProjects ep ON e.EmployeeID = ep.EmployeeID
LEFT JOIN Projects p ON ep.ProjectID = p.ProjectID
GROUP BY e.EmployeeID, e.FirstName, e.LastName, e.Email, d.DepartmentName, jt.JobTitleName
ORDER BY TotalProjects DESC, TotalAllocation DESC;

-- ============================================================================
-- QUERY 15: Financial analysis - Salary vs Performance correlation
-- ============================================================================
SELECT 
    e.FirstName,
    e.LastName,
    d.DepartmentName,
    jt.JobTitleName,
    e.Salary,
    COALESCE(pr.Rating, 0) as PerformanceRating,
    COALESCE(pr.Comments, 'No Review') as ReviewComments,
    CASE 
        WHEN e.Salary > (jt.MinSalary + jt.MaxSalary) / 2 THEN 'Above Mid-Range'
        ELSE 'Below Mid-Range'
    END as SalaryPosition,
    CASE 
        WHEN COALESCE(pr.Rating, 0) >= 4 THEN 'High Performer'
        WHEN COALESCE(pr.Rating, 0) >= 3 THEN 'Average Performer'
        ELSE 'Low Performer'
    END as PerformanceCategory
FROM Employees e
JOIN Departments d ON e.DepartmentID = d.DepartmentID
JOIN JobTitles jt ON e.JobTitleID = jt.JobTitleID
LEFT JOIN PerformanceReviews pr ON e.EmployeeID = pr.EmployeeID
ORDER BY e.Salary DESC;

-- ============================================================================
-- QUERY 16: Attendance pattern analysis by day of week
-- ============================================================================
SELECT 
    CASE strftime('%w', a.Date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END as DayOfWeek,
    COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) as PresentCount,
    COUNT(CASE WHEN a.Status = 'Absent' THEN 1 END) as AbsentCount,
    COUNT(CASE WHEN a.Status = 'OnLeave' THEN 1 END) as OnLeaveCount,
    COUNT(CASE WHEN a.Status = 'WFH' THEN 1 END) as WFHCount,
    COUNT(*) as TotalDays,
    ROUND(COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) * 100.0 / COUNT(*), 2) as AttendanceRate
FROM Attendance a
WHERE a.Date >= '2024-01-01' AND a.Date <= '2024-12-31'
GROUP BY strftime('%w', a.Date)
ORDER BY strftime('%w', a.Date);

-- ============================================================================
-- QUERY 17: Department cost efficiency analysis
-- ============================================================================
SELECT 
    d.DepartmentName,
    d.Location,
    COUNT(e.EmployeeID) as EmployeeCount,
    ROUND(SUM(e.Salary), 2) as TotalSalaryCost,
    ROUND(AVG(e.Salary), 2) as AverageSalary,
    ROUND(SUM(e.Salary) / COUNT(e.EmployeeID), 2) as CostPerEmployee,
    COUNT(p.ProjectID) as ActiveProjects,
    COALESCE(SUM(p.Budget), 0) as TotalProjectBudget,
    ROUND(SUM(e.Salary) / COALESCE(SUM(p.Budget), 1), 4) as SalaryToBudgetRatio
FROM Departments d
LEFT JOIN Employees e ON d.DepartmentID = e.DepartmentID
LEFT JOIN Projects p ON d.DepartmentID = p.DepartmentID AND date('now') BETWEEN p.StartDate AND p.EndDate
GROUP BY d.DepartmentID, d.DepartmentName, d.Location
ORDER BY TotalSalaryCost DESC;

-- ============================================================================
-- QUERY 18: Employee retention analysis by hire year
-- ============================================================================
SELECT 
    strftime('%Y', e.HireDate) as HireYear,
    COUNT(e.EmployeeID) as HiredCount,
    COUNT(CASE WHEN e.HireDate >= date('now', '-1 year') THEN 1 END) as HiredLastYear,
    COUNT(CASE WHEN e.HireDate >= date('now', '-2 years') THEN 1 END) as HiredLast2Years,
    COUNT(CASE WHEN e.HireDate >= date('now', '-5 years') THEN 1 END) as HiredLast5Years,
    ROUND(AVG(julianday('now') - julianday(e.HireDate)) / 365.25, 2) as AverageTenureYears,
    ROUND(COUNT(CASE WHEN e.HireDate >= date('now', '-1 year') THEN 1 END) * 100.0 / COUNT(*), 2) as RecentHiresPercentage
FROM Employees e
GROUP BY strftime('%Y', e.HireDate)
ORDER BY HireYear DESC;

-- ============================================================================
-- QUERY 19: Project success metrics and resource utilization
-- ============================================================================
SELECT 
    p.ProjectName,
    d.DepartmentName,
    p.StartDate,
    p.EndDate,
    p.Budget,
    COUNT(ep.EmployeeID) as TeamSize,
    SUM(ep.AllocationPercent) as TotalAllocation,
    ROUND(SUM(ep.AllocationPercent) / COUNT(ep.EmployeeID), 2) as AverageAllocationPerEmployee,
    ROUND(p.Budget / COUNT(ep.EmployeeID), 2) as BudgetPerTeamMember,
    CASE 
        WHEN date('now') < p.StartDate THEN 'Not Started'
        WHEN date('now') BETWEEN p.StartDate AND p.EndDate THEN 'In Progress'
        WHEN date('now') > p.EndDate THEN 'Completed'
        ELSE 'Unknown'
    END as ProjectStatus,
    CASE 
        WHEN SUM(ep.AllocationPercent) > 100 THEN 'Over-Allocated'
        WHEN SUM(ep.AllocationPercent) = 100 THEN 'Fully Allocated'
        ELSE 'Under-Allocated'
    END as AllocationStatus
FROM Projects p
JOIN Departments d ON p.DepartmentID = d.DepartmentID
LEFT JOIN EmployeeProjects ep ON p.ProjectID = ep.ProjectID
GROUP BY p.ProjectID, p.ProjectName, d.DepartmentName, p.StartDate, p.EndDate, p.Budget
ORDER BY p.StartDate;

-- ============================================================================
-- QUERY 20: Comprehensive employee dashboard summary
-- ============================================================================
SELECT 
    'Total Employees' as Metric,
    COUNT(e.EmployeeID) as Value,
    '' as Detail
FROM Employees e

UNION ALL

SELECT 
    'Total Departments' as Metric,
    COUNT(d.DepartmentID) as Value,
    '' as Detail
FROM Departments d

UNION ALL

SELECT 
    'Active Projects' as Metric,
    COUNT(p.ProjectID) as Value,
    '' as Detail
FROM Projects p
WHERE date('now') BETWEEN p.StartDate AND p.EndDate

UNION ALL

SELECT 
    'Average Salary' as Metric,
    ROUND(AVG(e.Salary), 2) as Value,
    'Across all employees' as Detail
FROM Employees e

UNION ALL

SELECT 
    'Total Payroll Cost (Q1 2024)' as Metric,
    ROUND(SUM(p.NetSalary), 2) as Value,
    'Net salary after deductions' as Detail
FROM Payroll p
WHERE p.Year = 2024 AND p.Month IN (1, 2, 3)

UNION ALL

SELECT 
    'Average Performance Rating' as Metric,
    ROUND(AVG(pr.Rating), 2) as Value,
    'Based on recent reviews' as Detail
FROM PerformanceReviews pr
WHERE pr.ReviewDate >= date('now', '-1 year')

UNION ALL

SELECT 
    'Leave Requests Pending' as Metric,
    COUNT(lr.LeaveID) as Value,
    'Awaiting approval' as Detail
FROM LeaveRequests lr
WHERE lr.Status = 'Pending'

UNION ALL

SELECT 
    'Most Expensive Department' as Metric,
    d.DepartmentName as Value,
    CONCAT('$', ROUND(SUM(e.Salary), 2), ' total salary cost') as Detail
FROM Employees e
JOIN Departments d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentID, d.DepartmentName
ORDER BY SUM(e.Salary) DESC
LIMIT 1;
