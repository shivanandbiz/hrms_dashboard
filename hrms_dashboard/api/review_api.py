"""
Review API
Handles pending approvals for reporting managers
"""

import frappe
from frappe import _

@frappe.whitelist()
def get_pending_reviews():
    """Get pending approvals for the current user (reporting manager)"""
    try:
        # Get employee record for current user
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
        if not employee:
            return {
                "success": False,
                "message": "Employee record not found for current user"
            }
        
        pending_items = []
        
        # 1. Get pending Leave Applications where current user is the approver
        leave_applications = frappe.db.sql("""
            SELECT 
                la.name,
                la.employee,
                la.employee_name,
                la.leave_type,
                la.from_date,
                la.to_date,
                la.total_leave_days,
                e.employee_name as emp_name
            FROM 
                `tabLeave Application` la
            INNER JOIN 
                `tabEmployee` e ON la.employee = e.name
            WHERE 
                la.docstatus = 0
                AND la.status IN ('Open', 'Pending')
                AND (la.leave_approver = %s OR e.reports_to = %s)
            ORDER BY 
                la.creation DESC
        """, (frappe.session.user, employee), as_dict=True)
        
        for la in leave_applications:
            # Get employee initials
            name_parts = la.emp_name.split()
            initials = ''.join([part[0].upper() for part in name_parts if part])
            
            pending_items.append({
                "doctype": "Leave Application",
                "name": la.name,
                "employee": la.employee,
                "employee_name": la.emp_name,
                "initials": initials,
                "description": f"{la.leave_type} ({la.total_leave_days} days)",
                "from_date": str(la.from_date),
                "to_date": str(la.to_date)
            })
        
        # 2. Get pending Attendance Requests
        attendance_requests = frappe.db.sql("""
            SELECT 
                ar.name,
                ar.employee,
                ar.employee_name,
                ar.from_date,
                ar.to_date,
                ar.reason,
                e.employee_name as emp_name
            FROM 
                `tabAttendance Request` ar
            INNER JOIN 
                `tabEmployee` e ON ar.employee = e.name
            WHERE 
                ar.docstatus = 0
                AND (e.reports_to = %s)
            ORDER BY 
                ar.creation DESC
        """, (employee,), as_dict=True)
        
        for ar in attendance_requests:
            # Get employee initials
            name_parts = ar.emp_name.split()
            initials = ''.join([part[0].upper() for part in name_parts if part])
            
            pending_items.append({
                "doctype": "Attendance Request",
                "name": ar.name,
                "employee": ar.employee,
                "employee_name": ar.emp_name,
                "initials": initials,
                "description": f"Attendance Request ({ar.reason or 'No reason'})",
                "from_date": str(ar.from_date),
                "to_date": str(ar.to_date) if ar.to_date else str(ar.from_date)
            })
        
        # 3. Get pending Expense Claims
        expense_claims = frappe.db.sql("""
            SELECT 
                ec.name,
                ec.employee,
                ec.employee_name,
                ec.total_claimed_amount,
                ec.posting_date,
                e.employee_name as emp_name
            FROM 
                `tabExpense Claim` ec
            INNER JOIN 
                `tabEmployee` e ON ec.employee = e.name
            WHERE 
                ec.docstatus = 0
                AND ec.approval_status IN ('Draft', 'Pending')
                AND (e.reports_to = %s)
            ORDER BY 
                ec.creation DESC
        """, (employee,), as_dict=True)
        
        for ec in expense_claims:
            # Get employee initials
            name_parts = ec.emp_name.split()
            initials = ''.join([part[0].upper() for part in name_parts if part])
            
            pending_items.append({
                "doctype": "Expense Claim",
                "name": ec.name,
                "employee": ec.employee,
                "employee_name": ec.emp_name,
                "initials": initials,
                "description": f"Expense Claim (₹{ec.total_claimed_amount})",
                "from_date": str(ec.posting_date),
                "to_date": str(ec.posting_date)
            })
        
        return {
            "success": True,
            "pending_items": pending_items,
            "total_count": len(pending_items)
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching pending reviews: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }
