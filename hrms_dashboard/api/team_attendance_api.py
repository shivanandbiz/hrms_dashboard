"""
Team Attendance Tracking API
Fetches attendance status of reporting employees
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, today, get_datetime

@frappe.whitelist()
def get_team_attendance_status():
    """Get attendance status of reporting employees (team members)"""
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
            fields=["name", "employee_name", "default_shift"]
        )
        
        if not reporting_employees:
            return {
                "success": True,
                "not_yet_in": [],
                "late_arrivals": [],
                "on_time": [],
                "total_team": 0,
                "message": "No reporting employees found"
            }
        
        not_yet_in = []
        late_arrivals = []
        on_time = []
        
        for emp in reporting_employees:
            emp_name = emp.get("name")
            emp_display_name = emp.get("employee_name")
            default_shift = emp.get("default_shift")
            
            # Get today's check-in record
            checkin = frappe.get_all(
                "Employee Checkin",
                filters={
                    "employee": emp_name,
                    "log_type": "IN",
                    "time": [">=", today()]
                },
                fields=["time"],
                order_by="time asc",
                limit=1
            )
            
            if not checkin:
                # No check-in yet
                not_yet_in.append({
                    "employee": emp_name,
                    "employee_name": emp_display_name,
                    "initials": get_initials(emp_display_name)
                })
            else:
                # Check if late based on shift timing
                checkin_time = checkin[0].get("time")
                is_late = False
                
                if default_shift:
                    try:
                        # Get shift start time
                        shift = frappe.get_doc("Shift Type", default_shift)
                        if shift and shift.start_time:
                            # Combine today's date with shift start time
                            shift_start = get_datetime(f"{today()} {shift.start_time}")
                            checkin_datetime = get_datetime(checkin_time)
                            
                            # Check if checked in after shift start time
                            if checkin_datetime > shift_start:
                                is_late = True
                    except Exception as e:
                        frappe.log_error(f"Error checking shift timing: {str(e)}")
                
                if is_late:
                    late_arrivals.append({
                        "employee": emp_name,
                        "employee_name": emp_display_name,
                        "initials": get_initials(emp_display_name),
                        "checkin_time": str(checkin_time)
                    })
                else:
                    on_time.append({
                        "employee": emp_name,
                        "employee_name": emp_display_name,
                        "initials": get_initials(emp_display_name),
                        "checkin_time": str(checkin_time)
                    })
        
        return {
            "success": True,
            "not_yet_in": not_yet_in,
            "late_arrivals": late_arrivals,
            "on_time": on_time,
            "total_team": len(reporting_employees)
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching team attendance: {str(e)}")
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
