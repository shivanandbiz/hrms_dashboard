"""
Test script to verify team attendance API is working correctly
Run this in ERPNext console or as a bench command
"""

import frappe
from hrms_dashboard.api.team_attendance_api import get_team_attendance_status

def test_team_attendance():
    """Test the team attendance API"""
    
    # Set the current user (replace with your user email)
    frappe.set_user("Administrator")  # Change this to the manager's email
    
    # Call the API
    result = get_team_attendance_status()
    
    print("\n" + "="*60)
    print("TEAM ATTENDANCE API TEST RESULTS")
    print("="*60)
    
    if result.get("success"):
        print(f"\n✓ Success: {result.get('success')}")
        print(f"Total Team Members: {result.get('total_team', 0)}")
        
        print("\n--- Not Yet In ---")
        for emp in result.get('not_yet_in', []):
            print(f"  • {emp['employee_name']} ({emp['initials']})")
        
        print("\n--- Late Arrivals ---")
        for emp in result.get('late_arrivals', []):
            print(f"  • {emp['employee_name']} ({emp['initials']})")
        
        print("\n--- On Time ---")
        for emp in result.get('on_time', []):
            print(f"  • {emp['employee_name']} ({emp['initials']})")
    else:
        print(f"\n✗ Error: {result.get('message')}")
    
    print("\n" + "="*60)
    print("RAW RESPONSE:")
    print("="*60)
    print(result)
    print("\n")

if __name__ == "__main__":
    test_team_attendance()
