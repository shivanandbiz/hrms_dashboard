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

# 1.1 Monkey patch get_holiday_dates_for_employee so attendance is marked for optional leaves
from frappe.utils import cstr
original_get_holiday_dates_for_employee = leave_application.get_holiday_dates_for_employee

def custom_get_holiday_dates_for_employee(employee, start_date, end_date):
	dates = original_get_holiday_dates_for_employee(employee, start_date, end_date)
	if dates and frappe.db.has_column("Holiday", "is_optional"):
		holiday_list = get_holiday_list_for_employee(employee)
		if holiday_list:
			optional_holidays = frappe.db.get_all(
				"Holiday",
				filters={"parent": holiday_list, "holiday_date": ("in", dates), "is_optional": 1},
				pluck="holiday_date"
			)
			if optional_holidays:
				optional_holidays_str = [cstr(d) for d in optional_holidays]
				dates = [d for d in dates if cstr(d) not in optional_holidays_str]
	return dates

leave_application.get_holiday_dates_for_employee = custom_get_holiday_dates_for_employee

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
