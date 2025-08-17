#!/usr/bin/env python3
"""
HR Database Management System - Test Script
This script tests the basic functionality of the system.
"""

import sqlite3
import os

def test_database_connection():
    """Test database connection and basic queries"""
    print("Testing database connection...")
    
    if not os.path.exists('hr_database.db'):
        print("❌ Database file not found! Please run 'python init_db.py' first.")
        return False
    
    try:
        conn = sqlite3.connect('hr_database.db')
        cursor = conn.cursor()
        print("✅ Database connection successful")
        
        # Test basic queries
        print("\nTesting basic queries...")
        
        # Count employees
        cursor.execute("SELECT COUNT(*) FROM Employees")
        emp_count = cursor.fetchone()[0]
        print(f"✅ Employees count: {emp_count}")
        
        # Count departments
        cursor.execute("SELECT COUNT(*) FROM Departments")
        dept_count = cursor.fetchone()[0]
        print(f"✅ Departments count: {dept_count}")
        
        # Count projects
        cursor.execute("SELECT COUNT(*) FROM Projects")
        proj_count = cursor.fetchone()[0]
        print(f"✅ Projects count: {proj_count}")
        
        # Test a complex query
        print("\nTesting complex query (top salaries by department)...")
        cursor.execute("""
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
            ORDER BY DepartmentName, SalaryRank
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        print(f"✅ Complex query successful, returned {len(results)} rows")
        
        # Show sample results
        if results:
            print("\nSample results:")
            for i, row in enumerate(results[:5]):
                print(f"  {i+1}. {row[0]} - {row[1]} {row[2]} (${row[3]:,.2f}) - Rank {row[4]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_cli_commands():
    """Test if CLI commands are available"""
    print("\nTesting CLI command availability...")
    
    try:
        import subprocess
        import sys
        
        # Test help command
        result = subprocess.run([sys.executable, 'hr_cli.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI help command works")
        else:
            print("❌ CLI help command failed")
            return False
        
        # Test status command
        result = subprocess.run([sys.executable, 'hr_cli.py', 'status'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI status command works")
        else:
            print("❌ CLI status command failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("HR Database Management System - System Test")
    print("=" * 60)
    
    # Test database
    db_test = test_database_connection()
    
    # Test CLI
    cli_test = test_cli_commands()
    
    print("\n" + "=" * 60)
    if db_test and cli_test:
        print("✅ All tests passed! System is working correctly.")
        print("✅ You can now use the CLI interface:")
        print("   python hr_cli.py --help")
        print("   python hr_cli.py status")
        print("   python hr_cli.py employee list")
        print("   python hr_cli.py query dashboard")
    else:
        print("❌ Some tests failed. Please check the system setup.")
        if not db_test:
            print("   - Database test failed. Run 'python init_db.py'")
        if not cli_test:
            print("   - CLI test failed. Check dependencies and file permissions")
    print("=" * 60)

if __name__ == "__main__":
    main()
