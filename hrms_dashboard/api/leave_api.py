"""
Leave Management API
Handles leave balance, applications, and team leave status
"""

import frappe
from frappe import _

@frappe.whitelist()
def get_leave_balance_summary():
    """Get leave balance summary for current employee - only 4 specific leave types"""
    try:
        # Get employee record for current user
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
        if not employee:
            return {
                "success": False,
                "message": "Employee record not found for current user"
            }
        
        # Define the 4 specific leave types to display
        specific_leave_types = [
            "Casual Leave",
            "Optional Leave", 
            "Compensatory Off",
            "Privilege Leave"
        ]
        
        leave_balances = []
        
        # Process each leave type individually to avoid duplicates
        for leave_type in specific_leave_types:
            # Get leave balance using Frappe's built-in function
            # This automatically considers all active allocations for the leave type
            from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
            
            available_leaves = get_leave_balance_on(
                employee=employee,
                leave_type=leave_type,
                date=frappe.utils.today(),
                consider_all_leaves_in_the_allocation_period=True
            )
            
            # Get the most recent/current allocation for this leave type
            current_allocation = frappe.get_all(
                "Leave Allocation",
                filters={
                    "employee": employee,
                    "docstatus": 1,
                    "leave_type": leave_type,
                    "from_date": ["<=", frappe.utils.today()],
                    "to_date": [">=", frappe.utils.today()]
                },
                fields=[
                    "total_leaves_allocated",
                    "new_leaves_allocated",
                    "from_date",
                    "to_date",
                    "unused_leaves"
                ],
                order_by="to_date desc",
                limit=1
            )
            
            if current_allocation:
                allocation = current_allocation[0]
                
                # Get total allocated leaves
                total_allocated = allocation.get("total_leaves_allocated") or allocation.get("new_leaves_allocated") or 0
                
                # Get expired leaves (unused leaves from previous allocation)
                expired_leaves = allocation.get("unused_leaves") or 0
                
                # Get used leaves (approved leave applications within current allocation period)
                used_leaves = frappe.db.sql("""
                    SELECT COALESCE(SUM(total_leave_days), 0) as used
                    FROM `tabLeave Application`
                    WHERE employee = %s
                    AND leave_type = %s
                    AND docstatus = 1
                    AND status = 'Approved'
                    AND from_date >= %s
                    AND to_date <= %s
                """, (employee, leave_type, allocation.get("from_date"), allocation.get("to_date")))[0][0] or 0
                
                # Get pending approval leaves
                pending_leaves = frappe.db.sql("""
                    SELECT COALESCE(SUM(total_leave_days), 0) as pending
                    FROM `tabLeave Application`
                    WHERE employee = %s
                    AND leave_type = %s
                    AND docstatus = 0
                    AND status IN ('Open', 'Pending')
                    AND from_date >= %s
                """, (employee, leave_type, allocation.get("from_date")))[0][0] or 0
                
                leave_balances.append({
                    "leave_type": leave_type,
                    "total_allocated": total_allocated,
                    "expired_leaves": expired_leaves,
                    "used_leaves": used_leaves,
                    "pending_approval": pending_leaves,
                    "available_leaves": available_leaves,
                    # Keep backward compatibility
                    "balance": available_leaves,
                    "granted": total_allocated,
                    "consumed": used_leaves
                })
            else:
                # No current allocation found, but still show the card with zero values
                leave_balances.append({
                    "leave_type": leave_type,
                    "total_allocated": 0,
                    "expired_leaves": 0,
                    "used_leaves": 0,
                    "pending_approval": 0,
                    "available_leaves": 0,
                    "balance": 0,
                    "granted": 0,
                    "consumed": 0
                })
        
        return {
            "success": True,
            "leave_balances": leave_balances
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching leave balance: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }


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
