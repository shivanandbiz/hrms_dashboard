"""
Payroll API
Handles salary slips, payslip download, and salary information
"""

import frappe
from frappe import _
from datetime import datetime


@frappe.whitelist()
def get_latest_payslip():
    """Get latest salary slip for current user"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee not found"}
        
        # Get latest salary slip
        latest_slip = frappe.get_all(
            "Salary Slip",
            filters={"employee": employee, "docstatus": 1},
            fields=["name", "start_date", "end_date", "gross_pay", "total_deduction", "net_pay", "payment_days"],
            order_by="start_date desc",
            limit=1
        )
        
        if not latest_slip:
            return {"error": "No salary slip found"}
        
        slip = latest_slip[0]
        
        # Get earnings and deductions breakdown
        earnings = frappe.get_all(
            "Salary Detail",
            filters={"parent": slip.name, "parentfield": "earnings"},
            fields=["salary_component", "amount"]
        )
        
        deductions = frappe.get_all(
            "Salary Detail",
            filters={"parent": slip.name, "parentfield": "deductions"},
            fields=["salary_component", "amount"]
        )
        
        return {
            "name": slip.name,
            "start_date": str(slip.start_date),
            "end_date": str(slip.end_date),
            "gross_pay": slip.gross_pay,
            "total_deduction": slip.total_deduction,
            "net_pay": slip.net_pay,
            "payment_days": slip.payment_days,
            "earnings": earnings,
            "deductions": deductions
        }
    except Exception as e:
        frappe.log_error(f"Error getting latest payslip: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def download_payslip(payslip_name=None):
    """Download salary slip PDF"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee not found"}
        
        # If no payslip name provided, get latest
        if not payslip_name:
            latest = frappe.get_value(
                "Salary Slip",
                {"employee": employee, "docstatus": 1},
                "name",
                order_by="start_date desc"
            )
            payslip_name = latest
        
        if not payslip_name:
            return {"error": "No salary slip found"}
        
        # Verify employee owns this payslip
        slip_employee = frappe.get_value("Salary Slip", payslip_name, "employee")
        if slip_employee != employee:
            return {"error": "Unauthorized access"}
        
        # Generate PDF
        pdf = frappe.get_print(
            "Salary Slip",
            payslip_name,
            print_format="Salary Slip",
            as_pdf=True
        )
        
        # Save to file
        file_name = f"Salary_Slip_{payslip_name}.pdf"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "content": pdf,
            "is_private": 1,
            "folder": "Home/Attachments"
        })
        file_doc.save()
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "file_name": file_name
        }
    except Exception as e:
        frappe.log_error(f"Error downloading payslip: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def get_payslip_history(limit=12):
    """Get salary slip history"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return []
        
        payslips = frappe.get_all(
            "Salary Slip",
            filters={"employee": employee, "docstatus": 1},
            fields=["name", "start_date", "end_date", "gross_pay", "total_deduction", "net_pay"],
            order_by="start_date desc",
            limit=limit
        )
        
        return payslips
    except Exception as e:
        frappe.log_error(f"Error getting payslip history: {str(e)}")
        return []


@frappe.whitelist()
def get_ytd_summary():
    """Get Year-to-Date salary summary"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        
        if not employee:
            return {"error": "Employee not found"}
        
        current_year = datetime.now().year
        
        # Get all payslips for current year
        payslips = frappe.get_all(
            "Salary Slip",
            filters={
                "employee": employee,
                "docstatus": 1,
                "start_date": [">=", f"{current_year}-01-01"]
            },
            fields=["gross_pay", "total_deduction", "net_pay"]
        )
        
        if not payslips:
            return {
                "total_gross": 0,
                "total_deduction": 0,
                "total_net": 0,
                "months_paid": 0
            }
        
        total_gross = sum([p.gross_pay for p in payslips])
        total_deduction = sum([p.total_deduction for p in payslips])
        total_net = sum([p.net_pay for p in payslips])
        
        return {
            "total_gross": total_gross,
            "total_deduction": total_deduction,
            "total_net": total_net,
            "months_paid": len(payslips),
            "year": current_year
        }
    except Exception as e:
        frappe.log_error(f"Error getting YTD summary: {str(e)}")
        return {"error": str(e)}
