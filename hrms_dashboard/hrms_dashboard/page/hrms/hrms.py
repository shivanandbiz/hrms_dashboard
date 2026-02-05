import frappe

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False

@frappe.whitelist()
def get_dashboard_html():
    """Return the HRMS dashboard HTML content"""
    html = """
    <div class="hrms-dashboard-container">

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
                    <button class="btn-secondary">View Swipes</button>
                    <button class="btn-primary" onclick="handleSignOut()">Sign Out</button>
                </div>
            </div>
        </div>

        <!-- Row 2: Middle widgets -->
        <div class="dashboard-row row-middle">
            <!-- Payslip Widget -->
            <div class="hrms-widget payslip-widget">
                <div class="widget-header">
                    <h3 class="widget-title">Payslip</h3>
                    <span class="view-link">→</span>
                </div>
                <div class="widget-content">
                    <div class="payslip-chart">
                        <svg width="120" height="120" viewBox="0 0 120 120">
                            <circle cx="60" cy="60" r="50" fill="none" stroke="#e0e0e0" stroke-width="15" />
                            <circle cx="60" cy="60" r="50" fill="none" stroke="#0d7377" stroke-width="15"
                                stroke-dasharray="314" stroke-dashoffset="78" transform="rotate(-90 60 60)" />
                        </svg>
                        <div class="chart-label">
                            <span class="month">Jan 2026</span>
                            <span class="paid-days">31<br><small>Paid Days</small></span>
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
                        <button class="btn-link">Download</button>
                        <button class="btn-link">Show Salary</button>
                    </div>
                </div>
            </div>

            <!-- Middle Column: Quick Access, Upcoming Holidays, Track -->
            <div class="middle-column">
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

