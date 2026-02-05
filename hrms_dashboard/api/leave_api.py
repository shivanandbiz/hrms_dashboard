"""
Leave Management API
Handles leave balance, applications, and team leave status
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_leave_balance():
    """Get current user's leave balance"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee not found"}
        
        # Get leave allocations
        leave_allocations = frappe.get_all(
            "Leave Allocation",
            filters={"employee": employee, "docstatus": 1},
            fields=["leave_type", "total_leaves_allocated", "new_leaves_allocated"]
        )
        
        # Get leave applications
        leave_applications = frappe.get_all(
            "Leave Application",
            filters={"employee": employee, "docstatus": 1},
            fields=["leave_type", "total_leave_days"]
        )
        
        # Calculate balance
        balance = {}
        for allocation in leave_allocations:
            leave_type = allocation.leave_type
            total = allocation.total_leaves_allocated or 0
            used = sum([app.total_leave_days for app in leave_applications if app.leave_type == leave_type])
            balance[leave_type] = {
                "total": total,
                "used": used,
                "remaining": total - used
            }
        
        return balance
    except Exception as e:
        frappe.log_error(f"Error getting leave balance: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def get_pending_leaves():
    """Get pending leave requests for approval"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return []
        
        # Get pending leave applications
        pending_leaves = frappe.get_all(
            "Leave Application",
            filters={"leave_approver": user, "docstatus": 0},
            fields=["name", "employee_name", "leave_type", "from_date", "to_date", "total_leave_days", "description"],
            order_by="creation desc"
        )
        
        return pending_leaves
    except Exception as e:
        frappe.log_error(f"Error getting pending leaves: {str(e)}")
        return []


@frappe.whitelist()
def get_team_on_leave():
    """Get team members currently on leave"""
    try:
        from datetime import datetime
        today = datetime.today().date()
        
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return []
        
        # Get department
        department = frappe.get_value("Employee", employee, "department")
        
        if not department:
            return []
        
        # Get team members on leave
        team_on_leave = frappe.db.sql("""
            SELECT 
                la.employee_name,
                la.leave_type,
                la.from_date,
                la.to_date,
                la.total_leave_days
            FROM 
                `tabLeave Application` la
            INNER JOIN 
                `tabEmployee` e ON la.employee = e.name
            WHERE 
                e.department = %s
                AND la.docstatus = 1
                AND la.from_date <= %s
                AND la.to_date >= %s
                AND la.employee != %s
            ORDER BY 
                la.from_date
        """, (department, today, today, employee), as_dict=True)
        
        return team_on_leave
    except Exception as e:
        frappe.log_error(f"Error getting team on leave: {str(e)}")
        return []


@frappe.whitelist()
def apply_leave(leave_type, from_date, to_date, half_day=0, description=""):
    """Apply for leave"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee not found"}
        
        # Create leave application
        leave_app = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": employee,
            "leave_type": leave_type,
            "from_date": from_date,
            "to_date": to_date,
            "half_day": half_day,
            "description": description
        })
        
        leave_app.insert()
        leave_app.submit()
        
        return {
            "success": True,
            "message": "Leave application submitted successfully",
            "leave_application": leave_app.name
        }
    except Exception as e:
        frappe.log_error(f"Error applying leave: {str(e)}")
        return {"error": str(e)}
