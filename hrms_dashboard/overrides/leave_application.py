import frappe
from frappe import _
from frappe.utils import getdate, add_days
from hrms.hr.doctype.leave_application import leave_application
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication, NotAnOptionalHoliday
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

# 1. Monkey patch get_holidays to exclude optional holidays
original_get_holidays = leave_application.get_holidays

def custom_get_holidays(employee, from_date, to_date, holiday_list=None):
	"""get holidays between two dates for the given employee"""
	if not holiday_list:
		holiday_list = get_holiday_list_for_employee(employee)

	query = """select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
		where h1.parent = h2.name and h1.holiday_date between %s and %s
		and h2.name = %s"""

	if frappe.db.has_column("Holiday", "is_optional"):
		query += " and (h1.is_optional is null or h1.is_optional = 0)"

	holidays = frappe.db.sql(
		query,
		(from_date, to_date, holiday_list),
	)[0][0]

	return holidays

leave_application.get_holidays = custom_get_holidays

# 2. Override LeaveApplication Class to adjust validate_optional_leave
class CustomLeaveApplication(LeaveApplication):
	def validate_optional_leave(self):
		day = getdate(self.from_date)

		if frappe.db.has_column("Holiday", "is_optional"):
			holiday_list = get_holiday_list_for_employee(self.employee)
			if not holiday_list:
				frappe.throw(_("Holiday List not set for employee {0}").format(self.employee))
			
			while day <= getdate(self.to_date):
				if not frappe.db.exists(
					{"doctype": "Holiday", "parent": holiday_list, "holiday_date": day, "is_optional": 1}
				):
					frappe.throw(
						_("{0} is not marked as an Optional Holiday").format(frappe.utils.formatdate(day)), NotAnOptionalHoliday
					)
				day = add_days(day, 1)
		else:
			# Fallback to standard logic if is_optional column does not exist
			super().validate_optional_leave()
