import frappe

def create_doctypes():
    if not frappe.db.exists("DocType", "HRMS Dashboard Reaction"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "HRMS Dashboard Reaction",
            "module": "HRMS Dashboard",
            "custom": 1,
            "fields": [
                {"fieldname": "activity_id", "fieldtype": "Data", "label": "Activity ID", "reqd": 1},
                {"fieldname": "emoji", "fieldtype": "Data", "label": "Emoji", "reqd": 1},
                {"fieldname": "user", "fieldtype": "Link", "options": "User", "label": "User", "reqd": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created DocType: HRMS Dashboard Reaction")

    if not frappe.db.exists("DocType", "HRMS Dashboard Comment"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "HRMS Dashboard Comment",
            "module": "HRMS Dashboard",
            "custom": 1,
            "fields": [
                {"fieldname": "activity_id", "fieldtype": "Data", "label": "Activity ID", "reqd": 1},
                {"fieldname": "comment_text", "fieldtype": "Small Text", "label": "Comment Text", "reqd": 1},
                {"fieldname": "user", "fieldtype": "Link", "options": "User", "label": "User", "reqd": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created DocType: HRMS Dashboard Comment")

