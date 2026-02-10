"""
Team Leave Tracking API
Fetches leave applications for reporting employees
"""

import frappe
from frappe import _
from frappe.utils import today

@frappe.whitelist()
def get_reporting_team_on_leave():
    """Get reporting employees who are on leave from today onwards"""
    try:
        # Get current user's employee record
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
        if not employee:
            return {
                "success": False,
                "message": "Employee record not found for current user"
            }
        
        # Get all employees who report to this employee
        reporting_employees = frappe.get_all(
            "Employee",
            filters={"reports_to": employee, "status": "Active"},
            fields=["name", "employee_name"]
        )
        
        if not reporting_employees:
            return {
                "success": True,
                "team_on_leave": [],
                "message": "No reporting employees found"
            }
        
        team_on_leave = []
        today_date = today()
        
        for emp in reporting_employees:
            # Get approved leave applications from today onwards
            leave_applications = frappe.get_all(
                "Leave Application",
                filters={
                    "employee": emp.get("name"),
                    "docstatus": 1,  # Approved
                    "status": "Approved",
                    "to_date": [">=", today_date]  # Leave ends today or in the future
                },
                fields=["leave_type", "from_date", "to_date", "total_leave_days"],
                order_by="from_date asc"
            )
            
            for leave in leave_applications:
                team_on_leave.append({
                    "employee": emp.get("name"),
                    "employee_name": emp.get("employee_name"),
                    "initials": get_initials(emp.get("employee_name")),
                    "leave_type": leave.get("leave_type"),
                    "from_date": str(leave.get("from_date")),
                    "to_date": str(leave.get("to_date")),
                    "total_days": leave.get("total_leave_days")
                })
        
        return {
            "success": True,
            "team_on_leave": team_on_leave,
            "total_count": len(team_on_leave)
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching reporting team on leave: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

def get_initials(name):
    """Get initials from employee name"""
    if not name:
        return "??"
    
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "??"
