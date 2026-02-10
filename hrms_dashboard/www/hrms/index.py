import frappe

def get_context(context):
    """Provide context for the HRMS dashboard web page"""
    context.no_cache = 1
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.throw("Please login to access HRMS Dashboard", frappe.PermissionError)
    
    # Get employee record for current user
    employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
    
    if not employee:
        context.show_sidebar = False
        context.error_message = "No Employee record found for your user account"
    else:
        context.show_sidebar = False
        context.employee = employee
