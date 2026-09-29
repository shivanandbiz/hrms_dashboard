import frappe
from hrms_dashboard.setup_activity_doctypes import create_doctypes

def execute():
    print("Creating activity doctypes...")
    create_doctypes()
    frappe.db.commit()
    print("Successfully created activity doctypes.")
