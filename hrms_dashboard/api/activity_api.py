import frappe
import json

@frappe.whitelist()
def get_activity_data(activity_ids):
    if isinstance(activity_ids, str):
        activity_ids = json.loads(activity_ids)
        
    if not activity_ids:
        return {}
        
    data = {}
    for aid in activity_ids:
        data[aid] = {"reactions": {}, "comments": []}
        
        # Get reactions
        reactions = frappe.get_all("HRMS Dashboard Reaction", filters={"activity_id": aid}, fields=["emoji"])
        for r in reactions:
            if r.emoji not in data[aid]["reactions"]:
                data[aid]["reactions"][r.emoji] = 0
            data[aid]["reactions"][r.emoji] += 1
            
        # Get comments
        comments = frappe.get_all("HRMS Dashboard Comment", filters={"activity_id": aid}, fields=["comment_text", "user", "creation"], order_by="creation asc")
        for c in comments:
            user_doc = frappe.get_doc("User", c.user)
            full_name = user_doc.full_name
            img = user_doc.user_image or "/assets/frappe/images/default-avatar.png"
            html = f'''
            <div class="comment-item" style="display:flex;gap:10px;margin-bottom:12px;">
                <img src="{img}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;">
                <div style="background:#f0f2f5;padding:8px 12px;border-radius:12px;flex:1;">
                    <div style="font-weight:600;font-size:13px;margin-bottom:2px;">{full_name}</div>
                    <div style="font-size:14px;">{c.comment_text}</div>
                </div>
            </div>
            '''
            data[aid]["comments"].append(html)
            
    return data

@frappe.whitelist()
def add_reaction(activity_id, emoji):
    user = frappe.session.user
    
    # Check if exists
    existing = frappe.get_all("HRMS Dashboard Reaction", filters={"activity_id": activity_id, "emoji": emoji, "user": user})
    
    if existing:
        # Remove
        frappe.delete_doc("HRMS Dashboard Reaction", existing[0].name, ignore_permissions=True)
        return {"action": "removed"}
    else:
        # Add
        doc = frappe.get_doc({
            "doctype": "HRMS Dashboard Reaction",
            "activity_id": activity_id,
            "emoji": emoji,
            "user": user
        })
        doc.insert(ignore_permissions=True)
        return {"action": "added"}
        
@frappe.whitelist()
def add_comment(activity_id, comment_text):
    user = frappe.session.user
    doc = frappe.get_doc({
        "doctype": "HRMS Dashboard Comment",
        "activity_id": activity_id,
        "comment_text": comment_text,
        "user": user
    })
    doc.insert(ignore_permissions=True)
    
    # Return html
    user_doc = frappe.get_doc("User", user)
    full_name = user_doc.full_name
    img = user_doc.user_image or "/assets/frappe/images/default-avatar.png"
    html = f'''
    <div class="comment-item" style="display:flex;gap:10px;margin-bottom:12px;">
        <img src="{img}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;">
        <div style="background:#f0f2f5;padding:8px 12px;border-radius:12px;flex:1;">
            <div style="font-weight:600;font-size:13px;margin-bottom:2px;">{full_name}</div>
            <div style="font-size:14px;">{comment_text}</div>
        </div>
    </div>
    '''
    return html
