import frappe
import json

@frappe.whitelist()
def get_activity_data(activity_ids):
    if isinstance(activity_ids, str):
        activity_ids = json.loads(activity_ids)
        
    if not activity_ids:
        return {}
        
    # Comments and Reactions have been removed
    data = {aid: {"reactions": {}, "comments": []} for aid in activity_ids}
    
    return data
