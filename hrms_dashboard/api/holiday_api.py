"""
Holiday List API
Fetches upcoming holidays from ERPNext Holiday List
"""

import frappe
from frappe import _
from frappe.utils import today, getdate, formatdate

@frappe.whitelist()
def get_upcoming_holidays(limit=None):
    """Get upcoming holidays from the employee's holiday list"""
    try:
        # Get current user's employee record
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, ["name", "holiday_list"])
        
        if not employee:
            return {
                "success": False,
                "message": "Employee record not found for current user"
            }
        
        employee_name, holiday_list = employee
        
        # If employee doesn't have a holiday list, get the default one
        if not holiday_list:
            holiday_list = frappe.get_value("Holiday List", {"is_default": 1}, "name")
        
        if not holiday_list:
            return {
                "success": True,
                "holidays": [],
                "message": "No holiday list found"
            }
        
        # Get upcoming holidays from the holiday list
        today_date = today()
        
        holidays = frappe.get_all(
            "Holiday",
            filters={
                "parent": holiday_list,
                "holiday_date": [">=", today_date]
            },
            fields=["holiday_date", "description", "is_optional", "weekly_off"],
            order_by="holiday_date asc",
            limit=100  # Fetch up to 100 holidays to cover the year
        )
        
        # Format the holidays and filter out weekly offs (regular weekends)
        formatted_holidays = []
        for holiday in holidays:
            holiday_date = getdate(holiday.get("holiday_date"))
            weekday = holiday_date.strftime("%A")
            
            # Skip weekly offs (regular Saturdays and Sundays)
            if holiday.get("weekly_off"):
                continue
            
            # Clean HTML from description
            description = holiday.get("description") or ""
            # Remove HTML tags
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()
            
            formatted_holidays.append({
                "date": str(holiday_date),
                "day": holiday_date.strftime("%d %b"),
                "weekday": weekday,
                "description": description,
                "formatted_date": formatdate(holiday_date, "dd MMM yyyy"),
                "is_optional": holiday.get("is_optional") or 0
            })
        
        return {
            "success": True,
            "holidays": formatted_holidays,
            "holiday_list": holiday_list
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching upcoming holidays: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }
