import frappe

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False

@frappe.whitelist()
def get_dashboard_html():
    """Return the HRMS dashboard HTML content"""
    from datetime import datetime
    import calendar
    from dateutil.relativedelta import relativedelta
    
    # Calculate previous month
    today = datetime.today()
    prev_month_date = today - relativedelta(months=1)
    prev_month_name = prev_month_date.strftime("%b %Y") # e.g. "May 2026"
    _, days_in_prev_month = calendar.monthrange(prev_month_date.year, prev_month_date.month)

    from frappe.utils import getdate
    today_date = getdate()
    
    # Birthdays this month
    birthdays = frappe.db.sql("""
        SELECT name, employee_name, image, date_of_birth as date
        FROM `tabEmployee`
        WHERE status = 'Active' AND date_of_birth IS NOT NULL
        AND MONTH(date_of_birth) = %s
    """, (today_date.month,), as_dict=True)
    
    # Anniversaries this month
    anniversaries = frappe.db.sql("""
        SELECT name, employee_name, image, date_of_joining as date
        FROM `tabEmployee`
        WHERE status = 'Active' AND date_of_joining IS NOT NULL
        AND MONTH(date_of_joining) = %s AND YEAR(date_of_joining) < %s
    """, (today_date.month, today_date.year), as_dict=True)
    
    activities = []
    for b in birthdays:
        b['type'] = 'Birthday'
        b['day'] = b['date'].day
        activities.append(b)
        
    for a in anniversaries:
        a['type'] = 'Anniversary'
        a['day'] = a['date'].day
        a['years'] = today_date.year - a['date'].year
        if a['years'] > 0:
            activities.append(a)
            
    # Sort by day descending (most recent first in this month)
    activities = sorted(activities, key=lambda x: x['day'], reverse=True)[:6]
    
    birthday_svg = """<svg width="100" height="100" viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; max-height: 100%;">
        <path d="M50 110 L150 70 L170 80 L70 120 Z" fill="none" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M50 110 L50 113 L70 123 L70 120 Z" fill="none" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M150 70 L150 73 L170 83 L170 80 Z" fill="none" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M70 123 L170 83" fill="none" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M75 95 L95 87 L110 93 L90 101 Z" fill="#fff" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M75 95 L75 105 L90 111 L90 101 Z" fill="#fff" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M90 111 L110 103 L110 93 L90 101 Z" fill="#fff" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M85 91 L100 97 M90 101 L90 111" stroke="#3498db" stroke-width="2.5"/>
        <path d="M120 78 L135 72 L145 76 L130 82 Z" fill="#fff" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M120 78 L122 88 L132 92 L130 82 Z" fill="#fff" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M132 92 L142 86 L145 76 L130 82 Z" fill="#fff" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
        <path d="M120 78 Q125 65 132 65 Q135 65 145 76" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <circle cx="130" cy="62" r="3" fill="#e74c3c" stroke="#2c3e50" stroke-width="1"/>
        <path d="M60 40 L65 35 M40 60 L45 55 M150 40 L155 35 M160 100 L165 95" stroke="#2c3e50" stroke-width="2" stroke-linecap="round"/>
        <ellipse cx="40" cy="70" rx="6" ry="8" fill="none" stroke="#2c3e50" stroke-width="2" transform="rotate(-15 40 70)"/>
        <path d="M38 78 L42 82 M40 80 Q45 90 35 100" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <ellipse cx="25" cy="65" rx="5" ry="7" fill="none" stroke="#2c3e50" stroke-width="2" transform="rotate(10 25 65)"/>
        <path d="M25 72 Q20 80 28 90" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M70 30 L80 35 L75 25 Z" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M85 28 L95 33 L90 23 Z" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M100 26 L110 31 L105 21 Z" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M65 28 Q90 15 115 28" fill="none" stroke="#2c3e50" stroke-width="1.5"/>
    </svg>"""

    anniversary_svg = """<svg width="100" height="100" viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; max-height: 100%;">
        <path d="M40 30 L40 20 M35 25 L45 25 M36 21 L44 29 M36 29 L44 21" stroke="#f1c40f" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M160 40 L160 30 M155 35 L165 35 M156 31 L164 39 M156 39 L164 31" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M140 20 L142 25 L147 25 L143 28 L145 33 L140 30 L135 33 L137 28 L133 25 L138 25 Z" fill="none" stroke="#2c3e50" stroke-width="1.5"/>
        <circle cx="100" cy="70" r="8" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M92 70 Q100 55 108 70 Q112 85 110 90 Q100 80 90 90 Q88 85 92 70" fill="none" stroke="#2c3e50" stroke-width="1.5"/>
        <path d="M90 90 Q100 85 110 90 L105 110 L95 110 Z" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M95 110 L92 130 M105 110 L108 130" stroke="#2c3e50" stroke-width="2" stroke-linecap="round"/>
        <path d="M92 88 Q85 80 80 60" fill="none" stroke="#2c3e50" stroke-width="2" stroke-linecap="round"/>
        <path d="M108 88 Q115 80 120 60" fill="none" stroke="#2c3e50" stroke-width="2" stroke-linecap="round"/>
        <path d="M60 110 L50 120 L55 125 L65 115 Z" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M60 110 L65 100 L75 105 L65 115 Z" fill="none" stroke="#2c3e50" stroke-width="2"/>
        <path d="M70 102 L75 90 M72 105 L85 95 M75 108 L85 105" stroke="#2c3e50" stroke-width="2" stroke-linecap="round"/>
    </svg>"""

    activities_cards_html = ""
    if not activities:
        activities_cards_html = """
        <div style="padding: 30px; text-align: center; color: #7f8c8d; font-size: 13px;">
            No birthdays or work anniversaries this month.
        </div>
        """
    else:
        for act in activities:
            emp_name = act.get('employee_name')
            img = act.get('image') or '/assets/frappe/images/default-avatar.png'
            
            if act['type'] == 'Birthday':
                title = f"Happy Birthday, {emp_name}!"
                msg = f"Happy Birthday {emp_name} , Have a great year ahead!"
                icon_svg = birthday_svg
            else:
                title = f"Congratulations, {emp_name}!"
                msg = f"Our congratulations to {emp_name} on completing {act['years']} successful year(s)."
                icon_svg = anniversary_svg
                
            activity_id = f"{act['type'].lower()}_{emp_name.replace(' ', '_')}_{today_date.year}"
                
            day_diff = today_date.day - act['day']
            if day_diff == 0:
                timeago = "Today"
            elif day_diff == 1:
                timeago = "1 day ago"
            elif day_diff == -1:
                timeago = "In 1 day"
            elif day_diff > 1:
                timeago = f"{day_diff} days ago"
            else:
                timeago = f"In {abs(day_diff)} days"

            activities_cards_html += f"""
            <div class="activity-card" data-activity-id="{activity_id}" style="border: 1px solid #e0e0e0; border-radius: 8px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 260px; display: flex; flex-direction: column; position: relative; flex-shrink: 0;">
                <div style="padding: 24px 20px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <img src="/assets/hrms_dashboard/biztechnosys_logo.png" alt="Biztechnosys" style="height: 30px; object-fit: contain;">
                            </div>
                            <div style="font-size: 12px; color: #7f8c8d;">Group: Events</div>
                        </div>
                        <span style="font-size: 11px; color: #95a5a6;">{timeago}</span>
                    </div>
                    <div style="display: flex; gap: 16px; align-items: center;">
                        <div style="width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;">
                            {icon_svg}
                        </div>
                        <div style="flex: 1;">
                            <p style="font-size: 13px; color: #2c3e50; margin: 0 0 12px 0; line-height: 1.4;">{msg}</p>
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <div style="width: 40px; height: 40px; border-radius: 50%; background: #e0e0e0; display: flex; align-items: center; justify-content: center; overflow: hidden; flex-shrink: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                    <img src="{img}" onerror="this.src='/assets/frappe/images/default-avatar.png'" style="width: 100%; height: 100%; object-fit: cover;">
                                </div>
                                <strong style="font-size: 13px; color: #2c3e50;">{title}</strong>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Footer Actions -->
                    <div class="activity-actions" style="border-top: 1px solid #eee; padding-top: 12px; display: flex; gap: 16px; margin-top: 16px; position: relative;">
                        <button class="btn-reaction" style="background: none; border: none; color: #7f8c8d; cursor: pointer; display: flex; align-items: center; gap: 6px; font-size: 13px; padding: 0;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
                            Reaction
                        </button>
                        <button class="btn-comment" style="background: none; border: none; color: #7f8c8d; cursor: pointer; display: flex; align-items: center; gap: 6px; font-size: 13px; padding: 0;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                            Comment
                        </button>
                        
                        <div class="reactions-picker" style="display: none; position: absolute; bottom: 100%; left: 0; background: white; border: 1px solid #ddd; border-radius: 20px; padding: 4px 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 10; gap: 8px;">
                            <span class="emoji-option" style="cursor: pointer; font-size: 20px;">👍</span>
                            <span class="emoji-option" style="cursor: pointer; font-size: 20px;">❤️</span>
                            <span class="emoji-option" style="cursor: pointer; font-size: 20px;">😂</span>
                            <span class="emoji-option" style="cursor: pointer; font-size: 20px;">🎉</span>
                            <span class="emoji-option" style="cursor: pointer; font-size: 20px;">👏</span>
                        </div>
                    </div>
                    
                    <div class="comments-section" style="display: none; margin-top: 12px; padding-top: 12px; border-top: 1px solid #eee;">
                        <div class="comments-list" style="max-height: 200px; overflow-y: auto; margin-bottom: 12px;"></div>
                        <div style="display: flex; gap: 8px;">
                            <input type="text" class="comment-input" placeholder="Write a comment..." style="flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 16px; outline: none; font-size: 13px;">
                            <button class="btn-submit-comment" style="background: #2196F3; color: white; border: none; padding: 6px 12px; border-radius: 16px; cursor: pointer; font-size: 13px;">Post</button>
                        </div>
                    </div>
                </div>
            </div>
            """

    html = f"""
    <div class="hrms-dashboard-container">
    
        <!-- Greeting & Quote Widget -->
        <div class="greeting-widget-container" style="background: white; border-radius: 8px; padding: 15px 25px; margin-bottom: 20px;">
            <h2 id="greeting-text" class="greeting-text" style="margin-top: 0; margin-bottom: 5px; font-size: 24px;">Good Morning</h2>
            <div class="quote-container" style="margin-top: 5px; border-left: 3px solid #3498db; padding-left: 10px;">
                <p id="quote-text" class="quote-text" style="font-size: 14px; margin-bottom: 3px; color: #5a6c7d;">The only impossible journey is the one you never begin.</p>
                <p id="quote-author" class="quote-author" style="font-size: 12px; color: #95a5a6; margin: 0;">- Tony Robbins</p>
            </div>
        </div>

        <!-- Leave Balance Cards Section -->
        <div class="leave-balance-section">
            <div class="leave-card">
                <div class="leave-card-header">
                    <span class="leave-type">Comp - Off</span>
                    <span class="leave-granted">Granted: <strong>1.5</strong></span>
                </div>
                <div class="leave-balance-display">
                    <div class="balance-number">1.5</div>
                    <div class="balance-label">Balance</div>
                </div>
                <a href="#" class="view-details-link">View Details</a>
                <div class="leave-consumed">0 of 1.5 Consumed</div>
            </div>

            <div class="leave-card">
                <div class="leave-card-header">
                    <span class="leave-type">Casual Leave</span>
                    <span class="leave-granted">Granted: <strong>2</strong></span>
                </div>
                <div class="leave-balance-display">
                    <div class="balance-number">02</div>
                    <div class="balance-label">Balance</div>
                </div>
                <a href="#" class="view-details-link">View Details</a>
                <div class="leave-consumed">0 of 2 Consumed</div>
            </div>

            <div class="leave-card">
                <div class="leave-card-header">
                    <span class="leave-type">Privilege Leave</span>
                    <span class="leave-granted">Granted: <strong>14.5</strong></span>
                </div>
                <div class="leave-balance-display">
                    <div class="balance-number">14.5</div>
                    <div class="balance-label">Balance</div>
                </div>
                <a href="#" class="view-details-link">View Details</a>
                <div class="leave-consumed">0 of 14.5 Consumed</div>
            </div>

            <div class="leave-card">
                <div class="leave-card-header">
                    <span class="leave-type">Optional Holiday</span>
                    <span class="leave-granted">Granted: <strong>2</strong></span>
                </div>
                <div class="leave-balance-display">
                    <div class="balance-number">02</div>
                    <div class="balance-label">Balance</div>
                </div>
                <a href="#" class="view-details-link">View Details</a>
                <div class="leave-consumed">0 of 2 Consumed</div>
            </div>
        </div>

        <!-- Row 1: Top 3 widgets -->
        <div class="dashboard-row row-top">
            <!-- Review Widget -->
            <div class="hrms-widget review-widget">
                <h3 class="widget-title">Review</h3>
                <div class="widget-content">
                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='20' y='10' width='60' height='80' fill='%23e3f2fd' stroke='%232196F3' stroke-width='2' rx='5'/%3E%3Cline x1='30' y1='30' x2='70' y2='30' stroke='%232196F3' stroke-width='2'/%3E%3Cline x1='30' y1='45' x2='70' y2='45' stroke='%232196F3' stroke-width='2'/%3E%3Cline x1='30' y1='60' x2='70' y2='60' stroke='%232196F3' stroke-width='2'/%3E%3C/svg%3E"
                        alt="Review" class="widget-icon">
                    <p class="widget-message">Hurrah! You've nothing to review.</p>
                </div>
            </div>

            <!-- Who is in Widget -->
            <div class="hrms-widget attendance-widget">
                <div class="widget-header">
                    <h3 class="widget-title">Who is in?</h3>
                    <span class="view-link">→</span>
                </div>
                <div class="widget-content">
                    <div class="attendance-status">
                        <div class="status-item">
                            <span class="status-label">Not Yet In</span>
                            <span class="status-badge badge-yellow">1</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Late Arrivals</span>
                            <span class="status-badge badge-red">1</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">On Time</span>
                        </div>
                        <p class="attendance-message">We couldn't find your team around</p>
                    </div>
                </div>
            </div>

            <!-- Clock Widget -->
            <div class="hrms-widget clock-widget">
                <h3 class="widget-title">5 February 2026</h3>
                <p class="widget-subtitle">Thursday | 10:00 A.m To 7:00 P.m</p>
                <div class="timer-display">
                    <span id="timer" class="timer">18:55:09</span>
                </div>
                <div class="widget-actions">
                    <button class="btn-view-swipes">View Swipes</button>
                    <button class="btn-sign-out">Sign In</button>
                </div>
            </div>
        </div>

        <!-- Row 2: Middle widgets -->
        <div class="dashboard-row row-middle">
            <!-- Payslip Widget -->
            <div class="hrms-widget payslip-widget">
                <div class="widget-header">
                    <h3 class="widget-title">Payslip</h3>
                    <select id="payslip-selector" style="margin-left: auto; margin-right: 10px; font-size: 12px; padding: 2px 5px; border: 1px solid #e0e0e0; border-radius: 4px; background: white; color: #333; outline: none; cursor: pointer;">
                    </select>
                    <span class="view-link" onclick="window.location.href='/app/salary-slip'" style="cursor: pointer;" title="View all Salary Slips">→</span>
                </div>
                <div class="widget-content">
                    <div class="payslip-chart">
                        <svg width="120" height="120" viewBox="0 0 120 120">
                            <circle cx="60" cy="60" r="50" fill="none" stroke="#e0e0e0" stroke-width="15" />
                            <circle cx="60" cy="60" r="50" fill="none" stroke="#0d7377" stroke-width="15"
                                stroke-dasharray="314" stroke-dashoffset="78" transform="rotate(-90 60 60)" />
                        </svg>
                        <div class="chart-label">
                            <span class="month">{prev_month_name}</span>
                            <span class="paid-days">{days_in_prev_month}<br><small>Paid Days</small></span>
                        </div>
                    </div>
                    <div class="payslip-breakdown">
                        <div class="breakdown-row">
                            <span class="label">Gross Pay</span>
                            <span class="value">*****</span>
                        </div>
                        <div class="breakdown-row">
                            <span class="label">Deduction</span>
                            <span class="value">*****</span>
                        </div>
                        <div class="breakdown-row">
                            <span class="label">Net Pay</span>
                            <span class="value">*****</span>
                        </div>
                    </div>
                    <div class="widget-actions">
                        <button class="btn-download">Download</button>
                        <button class="btn-show-salary">Show Salary</button>
                    </div>
                </div>
            </div>

            <!-- Middle Column: Activities, Quick Access, Upcoming Holidays, Track -->
            <div class="middle-column">
                <!-- Activities Feed -->
                <div class="hrms-widget activities-widget" style="padding: 0; display: flex; flex-direction: column;">
                    <div class="widget-header" style="padding: 16px 16px 10px 16px; border-bottom: 1px solid #f0f0f0; margin-bottom: 0; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center;">
                            <div style="width: 3px; height: 16px; background: #3498db; margin-right: 8px;"></div>
                            <h3 class="widget-title" style="font-size: 14px; font-weight: 500; color: #5a6c7d;">All Activities - All Groups</h3>
                        </div>
                        <div style="font-size: 12px; color: #5a6c7d; cursor: pointer; display: flex; align-items: center;">
                            Sort: <strong style="margin-left: 4px; margin-right: 4px; color: #2c3e50;">Newest first</strong> 
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </div>
                    </div>
                    <div class="widget-content feed-scroll-container" style="flex: 1; max-height: 450px; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 16px; align-items: stretch; background: #fafafa;">
                        {activities_cards_html}
                                            </div>
                </div>

                <!-- Quick Access -->
                <div class="hrms-widget quick-access-widget">
                    <h3 class="widget-title">Quick Access</h3>
                    <div class="widget-content">
                        <div class="quick-access-item">
                            <strong>Reimbursement Payslip</strong>
                            <p class="item-note">Use quick access to view important salary details.</p>
                        </div>
                        <div class="quick-access-item">IT Statement</div>
                        <div class="quick-access-item">YTD Reports</div>
                        <div class="quick-access-item">Loan Statement</div>
                    </div>
                </div>

                <!-- Upcoming Holidays -->
                <div class="hrms-widget holidays-widget">
                    <div class="widget-header">
                        <h3 class="widget-title">Upcoming Holidays</h3>
                        <span class="view-link">→</span>
                    </div>
                    <div class="widget-content">
                        <div class="holiday-item">
                            <div class="holiday-info">
                                <strong>04 Mar</strong> Wednesday<br>
                                <span class="holiday-name">Holi</span>
                            </div>
                            <button class="btn-apply">Apply</button>
                        </div>
                        <div class="holiday-item">
                            <div class="holiday-info">
                                <strong>19 Mar</strong> Thursday<br>
                                <span class="holiday-name">Ugadi</span>
                            </div>
                        </div>
                        <div class="holiday-item">
                            <div class="holiday-info">
                                <strong>03 Apr</strong> Friday<br>
                                <span class="holiday-name">Good Friday</span>
                            </div>
                            <button class="btn-apply">Apply</button>
                        </div>
                        <div class="holiday-item">
                            <div class="holiday-info">
                                <strong>15 Apr</strong> Wednesday<br>
                                <span class="holiday-name">Vishu</span>
                            </div>
                            <button class="btn-apply">Apply</button>
                        </div>
                    </div>
                </div>

                <!-- Track Widget -->
                <div class="hrms-widget track-widget">
                    <h3 class="widget-title">Track</h3>
                    <div class="widget-content">
                        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M30,50 L40,60 L70,30' fill='none' stroke='%234CAF50' stroke-width='5'/%3E%3Ccircle cx='50' cy='50' r='40' fill='none' stroke='%234CAF50' stroke-width='3'/%3E%3C/svg%3E"
                            alt="Track" class="widget-icon-small">
                        <p class="widget-message">All good! You've nothing new to track.</p>
                    </div>
                </div>
            </div>

            <!-- Right Column: Team on Leave, POI, IT Declaration -->
            <div class="right-column">
                <!-- Team on Leave -->
                <div class="hrms-widget leave-widget">
                    <div class="widget-header">
                        <h3 class="widget-title">Team On Leave</h3>
                        <span class="view-link">→</span>
                    </div>
                    <div class="widget-content">
                        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='30' cy='70' r='8' fill='%23ff9800'/%3E%3Cpath d='M30,50 Q40,30 50,50 T70,50' fill='none' stroke='%23ff9800' stroke-width='3'/%3E%3Ccircle cx='80' cy='30' r='15' fill='%23fff59d' stroke='%23ff9800' stroke-width='2'/%3E%3C/svg%3E"
                            alt="Leave" class="widget-icon">
                        <p class="widget-message">It's empty here! No one in your team is on leave.</p>
                    </div>
                </div>

                <!-- POI Widget -->
                <div class="hrms-widget poi-widget">
                    <h3 class="widget-title">POI</h3>
                    <div class="widget-content">
                        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='25' y='20' width='50' height='60' fill='%23e3f2fd' stroke='%232196F3' stroke-width='2' rx='3'/%3E%3Cline x1='35' y1='35' x2='65' y2='35' stroke='%232196F3' stroke-width='2'/%3E%3Cline x1='35' y1='50' x2='65' y2='50' stroke='%232196F3' stroke-width='2'/%3E%3C/svg%3E"
                            alt="POI" class="widget-icon-small">
                        <p class="widget-message">Hold on! You can submit your Proof of Investments (POI) once released.
                        </p>
                    </div>
                </div>

                <!-- IT Declaration Widget -->
                <div class="hrms-widget it-widget">
                    <h3 class="widget-title">IT Declaration</h3>
                    <div class="widget-content">
                        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='25' y='20' width='50' height='60' fill='%23e3f2fd' stroke='%232196F3' stroke-width='2' rx='3'/%3E%3Ctext x='50' y='55' font-size='20' text-anchor='middle' fill='%232196F3'%3EIT%3C/text%3E%3C/svg%3E"
                            alt="IT" class="widget-icon-small">
                        <p class="widget-message">Hold on! You can submit your Income Tax (IT) declaration once
                            released.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return html

