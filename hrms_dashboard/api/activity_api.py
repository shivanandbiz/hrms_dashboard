import frappe
from frappe.utils import get_url_to_form

@frappe.whitelist()
def add_reaction(activity_id, emoji):
    # Check if user already reacted with this emoji
    existing = frappe.db.exists("HRMS Dashboard Reaction", {
        "activity_id": activity_id,
        "emoji": emoji,
        "user": frappe.session.user
    })
    
    if existing:
        # If they already reacted, maybe toggle it off? Or just ignore.
        frappe.delete_doc("HRMS Dashboard Reaction", existing)
        return {"action": "removed"}
    else:
        doc = frappe.get_doc({
            "doctype": "HRMS Dashboard Reaction",
            "activity_id": activity_id,
            "emoji": emoji,
            "user": frappe.session.user
        })
        doc.insert(ignore_permissions=True)
        return {"action": "added"}

@frappe.whitelist()
def add_comment(activity_id, comment_text):
    if not comment_text:
        return
        
    doc = frappe.get_doc({
        "doctype": "HRMS Dashboard Comment",
        "activity_id": activity_id,
        "comment_text": comment_text,
        "user": frappe.session.user
    })
    doc.insert(ignore_permissions=True)
    
    return get_comment_html(doc)

def get_comment_html(doc):
    user_info = frappe.db.get_value("User", doc.user, ["full_name", "user_image"], as_dict=True)
    full_name = user_info.full_name if user_info else doc.user
    avatar_url = user_info.user_image if user_info and user_info.user_image else f"https://ui-avatars.com/api/?name={full_name}&background=random"
    
    return f"""
        <div class="activity-comment-item" style="display: flex; gap: 8px; margin-bottom: 8px;">
            <div style="width: 24px; height: 24px; border-radius: 50%; background: #e0e0e0; overflow: hidden; flex-shrink: 0;">
                <img src="{avatar_url}" onerror="this.src='https://ui-avatars.com/api/?name={full_name}&background=random'" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="background: white; padding: 8px 12px; border-radius: 12px; border: 1px solid #f0f0f0; font-size: 13px; color: #2c3e50; flex: 1;">
                <strong style="display: block; margin-bottom: 2px;">{full_name}</strong>
                <div>{doc.comment_text}</div>
            </div>
        </div>
    """

import json

@frappe.whitelist()
def get_activity_data(activity_ids):
    if isinstance(activity_ids, str):
        activity_ids = json.loads(activity_ids)
        
    if not activity_ids:
        return {}
        
    # Get all reactions
    reactions = frappe.get_all("HRMS Dashboard Reaction", 
        filters={"activity_id": ["in", activity_ids]},
        fields=["activity_id", "emoji", "user"]
    )
    
    # Get all comments
    comments = frappe.get_all("HRMS Dashboard Comment",
        filters={"activity_id": ["in", activity_ids]},
        fields=["name", "activity_id", "comment_text", "user"],
        order_by="creation asc"
    )
    
    data = {aid: {"reactions": {}, "comments": []} for aid in activity_ids}
    
    for r in reactions:
        aid = r.activity_id
        emoji = r.emoji
        if emoji not in data[aid]["reactions"]:
            data[aid]["reactions"][emoji] = []
        data[aid]["reactions"][emoji].append(r.user)
        
    for c in comments:
        doc = frappe.get_doc("HRMS Dashboard Comment", c.name)
        data[c.activity_id]["comments"].append(get_comment_html(doc))
        
    return data
