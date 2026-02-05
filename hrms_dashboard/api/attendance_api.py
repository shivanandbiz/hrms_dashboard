"""
Attendance API - ERPNext Integration
Handles attendance status, clock in/out using ERPNext Checkin
"""

import frappe
from frappe import _
from datetime import datetime, date, time
from frappe.utils import now_datetime, get_datetime, today


@frappe.whitelist()
def get_attendance_status():
    """Get current attendance status for the team using ERPNext data"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee record not found for current user"}
        
        # Get department
        department = frappe.get_value("Employee", employee, "department")
        
        if not department:
            return {"not_yet_in": 0, "late_arrivals": 0, "on_time": 0, "team_members": []}
        
        today_date = today()
        
        # Get team members from same department
        team_employees = frappe.get_all(
            "Employee",
            filters={"department": department, "status": "Active"},
            fields=["name", "employee_name", "user_id"]
        )
        
        not_yet_in = 0
        late_arrivals = 0
        on_time = 0
        team_data = []
        
        for emp in team_employees:
            # Check if employee has checked in today using Employee Checkin
            checkin = frappe.get_all(
                "Employee Checkin",
                filters={
                    "employee": emp.name,
                    "time": [">=", today_date],
                    "log_type": "IN"
                },
                fields=["time", "log_type"],
                order_by="time asc",
                limit=1
            )
            
            if checkin:
                checkin_time = get_datetime(checkin[0].time).time()
                # Consider late if after 10:00 AM
                if checkin_time > time(10, 0):
                    late_arrivals += 1
                    status = "Late"
                else:
                    on_time += 1
                    status = "On Time"
                    
                team_data.append({
                    "employee_name": emp.employee_name,
                    "status": status,
                    "checkin_time": str(checkin_time)
                })
            else:
                not_yet_in += 1
                team_data.append({
                    "employee_name": emp.employee_name,
                    "status": "Not Yet In",
                    "checkin_time": None
                })
        
        return {
            "not_yet_in": not_yet_in,
            "late_arrivals": late_arrivals,
            "on_time": on_time,
            "team_members": team_data
        }
    except Exception as e:
        frappe.log_error(f"Error getting attendance status: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def clock_in():
    """Clock in using ERPNext Employee Checkin"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee record not found"}
        
        # Check if already checked in today
        today_date = today()
        existing_checkin = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee,
                "time": [">=", today_date],
                "log_type": "IN"
            },
            limit=1
        )
        
        if existing_checkin:
            return {"error": "Already checked in today", "already_checked_in": True}
        
        # Create Employee Checkin record
        checkin = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": employee,
            "log_type": "IN",
            "time": now_datetime(),
            "device_id": "HRMS Dashboard"
        })
        checkin.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Checked in successfully",
            "checkin_time": str(checkin.time),
            "employee": employee
        }
    except Exception as e:
        frappe.log_error(f"Error checking in: {str(e)}")
        frappe.db.rollback()
        return {"error": str(e)}


@frappe.whitelist()
def clock_out():
    """Clock out using ERPNext Employee Checkin"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee record not found"}
        
        # Check if checked in today
        today_date = today()
        checkin_record = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee,
                "time": [">=", today_date],
                "log_type": "IN"
            },
            limit=1
        )
        
        if not checkin_record:
            return {"error": "No check-in record found for today"}
        
        # Check if already checked out
        checkout_record = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee,
                "time": [">=", today_date],
                "log_type": "OUT"
            },
            limit=1
        )
        
        if checkout_record:
            return {"error": "Already checked out today", "already_checked_out": True}
        
        # Create Employee Checkin record for OUT
        checkout = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": employee,
            "log_type": "OUT",
            "time": now_datetime(),
            "device_id": "HRMS Dashboard"
        })
        checkout.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Checked out successfully",
            "checkout_time": str(checkout.time),
            "employee": employee
        }
    except Exception as e:
        frappe.log_error(f"Error checking out: {str(e)}")
        frappe.db.rollback()
        return {"error": str(e)}


@frappe.whitelist()
def get_checkin_status():
    """Get today's check-in/out status for current user"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee record not found"}
        
        today_date = today()
        
        # Get check-in record
        checkin = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee,
                "time": [">=", today_date],
                "log_type": "IN"
            },
            fields=["time"],
            order_by="time asc",
            limit=1
        )
        
        # Get check-out record
        checkout = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee,
                "time": [">=", today_date],
                "log_type": "OUT"
            },
            fields=["time"],
            order_by="time desc",
            limit=1
        )
        
        return {
            "checked_in": bool(checkin),
            "checked_out": bool(checkout),
            "checkin_time": str(checkin[0].time) if checkin else None,
            "checkout_time": str(checkout[0].time) if checkout else None
        }
    except Exception as e:
        frappe.log_error(f"Error getting checkin status: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def get_attendance_history(from_date=None, to_date=None, limit=30):
    """Get attendance history using Employee Checkin records"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return []
        
        filters = {"employee": employee}
        
        if from_date:
            filters["time"] = [">=", from_date]
        if to_date:
            if "time" in filters:
                filters["time"] = ["between", [from_date, to_date]]
            else:
                filters["time"] = ["<=", to_date]
        
        # Get all checkin records
        checkins = frappe.get_all(
            "Employee Checkin",
            filters=filters,
            fields=["time", "log_type", "device_id"],
            order_by="time desc",
            limit=limit * 2  # Get more to group by date
        )
        
        # Group by date
        attendance_by_date = {}
        for record in checkins:
            date_str = str(get_datetime(record.time).date())
            if date_str not in attendance_by_date:
                attendance_by_date[date_str] = {"date": date_str, "checkin": None, "checkout": None}
            
            if record.log_type == "IN" and not attendance_by_date[date_str]["checkin"]:
                attendance_by_date[date_str]["checkin"] = str(get_datetime(record.time).time())
            elif record.log_type == "OUT":
                attendance_by_date[date_str]["checkout"] = str(get_datetime(record.time).time())
        
        # Convert to list and limit
        history = list(attendance_by_date.values())[:limit]
        
        return history
    except Exception as e:
        frappe.log_error(f"Error getting attendance history: {str(e)}")
        return []
