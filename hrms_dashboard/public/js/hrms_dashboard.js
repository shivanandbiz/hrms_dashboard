/**
 * HRMS Dashboard - JavaScript with ERPNext Integration
 * Handles timer, real API calls, and interactive features
 */

// Global state
let timerInterval = null;
let currentEmployee = null;

// Hide team widgets for regular employees
async function hideTeamWidgetsForEmployees() {
    try {
        // Check if user has reporting employees
        const response = await fetch('/api/method/hrms_dashboard.api.team_attendance_api.get_team_attendance_status');
        const data = await response.json();

        // If user has no reporting employees or is not a manager, hide team widgets
        if (!data.message || !data.message.success || data.message.total_team === 0) {
            // Hide "Who is in?" widget
            const attendanceWidget = document.querySelector('.attendance-widget');
            if (attendanceWidget) {
                attendanceWidget.style.display = 'none';
            }

            // Hide "Team On Leave" widget
            const leaveWidget = document.querySelector('.leave-widget');
            if (leaveWidget) {
                leaveWidget.style.display = 'none';
            }

            console.log('Team widgets hidden - user is not a manager or has no reporting employees');
            return false; // Not a manager
        }

        return true; // Is a manager
    } catch (error) {
        console.error('Error checking manager status:', error);
        // Hide team widgets on error to be safe
        const attendanceWidget = document.querySelector('.attendance-widget');
        const leaveWidget = document.querySelector('.leave-widget');
        if (attendanceWidget) attendanceWidget.style.display = 'none';
        if (leaveWidget) leaveWidget.style.display = 'none';
        return false;
    }
}

// Timer functionality
function startTimer() {
    const timerElement = document.getElementById('timer');
    if (!timerElement) return;

    function updateTimer() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        timerElement.textContent = `${hours}:${minutes}:${seconds}`;
    }

    updateTimer();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(updateTimer, 1000);
}

// Update clock widget date
function updateClockDate() {
    const clockWidget = document.querySelector('.clock-widget .widget-title');
    const clockSubtitle = document.querySelector('.clock-widget .widget-subtitle');

    if (clockWidget) {
        const now = new Date();
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        const dateStr = now.toLocaleDateString('en-GB', options);
        clockWidget.textContent = dateStr;
    }

    if (clockSubtitle) {
        const now = new Date();
        const weekday = now.toLocaleDateString('en-US', { weekday: 'long' });
        clockSubtitle.textContent = `${weekday} | 10:00 A.m To 7:00 P.m`;
    }
}

// Load Team Attendance Data (Who is in?) - Only for managers
async function loadAttendanceData() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.team_attendance_api.get_team_attendance_status');
        const data = await response.json();

        console.log('Team attendance response:', data);

        if (data.message && data.message.success) {
            updateAttendanceWidget(data.message);
        } else {
            console.log('Team attendance:', data.message?.message || 'No reporting employees');
            // Still update widget to show empty state
            if (data.message) {
                updateAttendanceWidget(data.message);
            }
        }
    } catch (error) {
        console.error('Error loading team attendance:', error);
    }
}

// Update attendance widget with team data
function updateAttendanceWidget(data) {
    const attendanceWidget = document.querySelector('.attendance-widget .widget-content');
    if (!attendanceWidget) return;

    const notYetInCount = data.not_yet_in?.length || 0;
    const lateArrivalsCount = data.late_arrivals?.length || 0;
    const onTimeCount = data.on_time?.length || 0;

    let html = '<div class="attendance-status">';

    // Not Yet In
    html += `
        <div class="status-item">
            <span class="status-label">Not Yet In</span>
            <span class="status-badge badge-yellow">${notYetInCount}</span>
        </div>
    `;

    // Show initials for Not Yet In employees
    if (notYetInCount > 0) {
        html += '<div class="employee-initials">';
        data.not_yet_in.forEach(emp => {
            html += `<span class="initial-badge badge-yellow" title="${emp.employee_name}">${emp.initials}</span>`;
        });
        html += '</div>';
    }

    // Late Arrivals
    html += `
        <div class="status-item">
            <span class="status-label">Late Arrivals</span>
            <span class="status-badge badge-red">${lateArrivalsCount}</span>
        </div>
    `;

    // Show initials for Late Arrivals
    if (lateArrivalsCount > 0) {
        html += '<div class="employee-initials">';
        data.late_arrivals.forEach(emp => {
            html += `<span class="initial-badge badge-red" title="${emp.employee_name}">${emp.initials}</span>`;
        });
        html += '</div>';
    }

    // On Time
    html += `
        <div class="status-item">
            <span class="status-label">On Time</span>
            ${onTimeCount > 0 ? `<span class="status-badge badge-green">${onTimeCount}</span>` : ''}
        </div>
    `;

    html += '</div>';

    // Message
    const totalTeam = data.total_team || 0;
    if (totalTeam === 0 || data.total_team === undefined || data.total_team === null) {
        html += '<p class="attendance-message">We couldn\'t find your team around</p>';
    } else {
        html += `<p class="attendance-message">${totalTeam} team member(s) tracked today</p>`;
    }

    attendanceWidget.innerHTML = html;
}

// Check current check-in status
async function checkCheckinStatus() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.attendance_api.get_checkin_status');
        const data = await response.json();

        if (data.message && !data.message.error) {
            updateCheckinButtons(data.message);
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Load Leave Balance Cards
function loadLeaveBalances() {
    frappe.call({
        method: 'hrms_dashboard.api.leave_api.get_leave_balance_summary',
        callback: function (r) {
            if (r.message && r.message.success) {
                updateLeaveBalanceCards(r.message.leave_balances);
            } else {
                console.error('Leave balance error:', r.message?.message || 'Unknown error');
            }
        }
    });
}

// Update Leave Balance Cards with real data
function updateLeaveBalanceCards(leaveBalances) {
    const leaveSection = document.querySelector('.leave-balance-section');
    if (!leaveSection) return;

    // Clear existing cards
    leaveSection.innerHTML = '';

    // Display all 4 leave types (they are already limited in the API)
    leaveBalances.forEach(leave => {
        const card = document.createElement('div');
        card.className = 'leave-card';

        const totalAllocated = parseFloat(leave.total_allocated || 0).toFixed(1);
        const expiredLeaves = parseFloat(leave.expired_leaves || 0).toFixed(1);
        const usedLeaves = parseFloat(leave.used_leaves || 0).toFixed(1);
        const pendingApproval = parseFloat(leave.pending_approval || 0).toFixed(1);
        const availableLeaves = parseFloat(leave.available_leaves || 0).toFixed(1);

        card.innerHTML = `
            <div class="leave-card-header">
                <span class="leave-type">${leave.leave_type}</span>
                <span class="leave-granted">Allocated: <strong>${totalAllocated}</strong></span>
            </div>
            <div class="leave-balance-display">
                <div class="balance-number">${availableLeaves}</div>
                <div class="balance-label">Available</div>
            </div>
            <div class="leave-details-grid">
                ${expiredLeaves > 0 ? `<div class="leave-detail-item">
                    <span class="detail-label">Expired:</span>
                    <span class="detail-value">${expiredLeaves}</span>
                </div>` : ''}
                <div class="leave-detail-item">
                    <span class="detail-label">Used:</span>
                    <span class="detail-value">${usedLeaves}</span>
                </div>
                ${pendingApproval > 0 ? `<div class="leave-detail-item">
                    <span class="detail-label">Pending:</span>
                    <span class="detail-value pending">${pendingApproval}</span>
                </div>` : ''}
            </div>
            <a href="/app/leave-application/new-leave-application-1?leave_type=${encodeURIComponent(leave.leave_type)}" class="view-details-link">Apply Leave</a>
        `;

        leaveSection.appendChild(card);
    });

    // If no leave allocations found, show a message
    if (leaveBalances.length === 0) {
        leaveSection.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #7f8c8d;">
                <p>No leave allocations found for your employee record.</p>
            </div>
        `;
    }
}

// Update check-in/out buttons based on status
function updateCheckinButtons(status) {
    const signOutBtn = document.querySelector('.btn-sign-out');
    const viewSwipesBtn = document.querySelector('.btn-view-swipes');

    if (signOutBtn) {
        // Store the current status in a data attribute for the event handler
        if (status.checked_in && !status.checked_out) {
            signOutBtn.textContent = 'Sign Out';
            signOutBtn.disabled = false;
            signOutBtn.style.opacity = '1';
            signOutBtn.dataset.action = 'signout';
        } else if (status.checked_out) {
            signOutBtn.textContent = 'Signed Out';
            signOutBtn.disabled = true;
            signOutBtn.style.opacity = '0.5';
            signOutBtn.dataset.action = 'none';
        } else {
            signOutBtn.textContent = 'Sign In';
            signOutBtn.disabled = false;
            signOutBtn.style.opacity = '1';
            signOutBtn.dataset.action = 'signin';
        }
    }

    // Update view swipes button to show actual checkin time
    if (viewSwipesBtn && status.checkin_time) {
        const time = new Date(status.checkin_time);
        const timeStr = time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        viewSwipesBtn.textContent = `In: ${timeStr}`;
    }
}

// Load leave data from ERPNext
async function loadLeaveData() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.leave_api.get_team_on_leave');
        const data = await response.json();

        if (data.message && !data.message.error) {
            updateLeaveWidget(data.message);
        }
    } catch (error) {
        console.error('Error loading leave data:', error);
    }
}

// Update leave widget with real data
function updateLeaveWidget(data) {
    const leaveWidget = document.querySelector('.leave-widget .widget-content');
    if (!leaveWidget) return;

    if (data && data.length > 0) {
        // Show team members on leave
        const leaveList = data.map(leave =>
            `<div class="leave-item">
                <strong>${leave.employee_name}</strong>
                <span>${leave.leave_type} (${leave.total_leave_days} days)</span>
            </div>`
        ).join('');

        leaveWidget.innerHTML = leaveList;
    }
}

// Load payslip data from ERPNext
async function loadPayslipData() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.payroll_api.get_latest_payslip');
        const data = await response.json();

        if (data.message && !data.message.error) {
            updatePayslipWidget(data.message);
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error loading payslip:', error);
        return false;
    }
}

// Update payslip widget with real data
function updatePayslipWidget(data) {
    if (!data || data.error) return;

    // Update breakdown values
    const grossPay = document.querySelector('.breakdown-row:nth-child(1) .value');
    const deduction = document.querySelector('.breakdown-row:nth-child(2) .value');
    const netPay = document.querySelector('.breakdown-row:nth-child(3) .value');

    if (grossPay && data.gross_pay) {
        grossPay.textContent = `₹${Math.round(data.gross_pay).toLocaleString()}`;
        grossPay.dataset.value = data.gross_pay;
    }
    if (deduction && data.total_deduction) {
        deduction.textContent = `₹${Math.round(data.total_deduction).toLocaleString()}`;
        deduction.dataset.value = data.total_deduction;
    }
    if (netPay && data.net_pay) {
        netPay.textContent = `₹${Math.round(data.net_pay).toLocaleString()}`;
        netPay.dataset.value = data.net_pay;
    }

    // Update paid days
    const paidDaysElement = document.querySelector('.paid-days');
    if (paidDaysElement && data.payment_days) {
        paidDaysElement.innerHTML = `${data.payment_days}<br><small>Paid Days</small>`;
    }
}

// Handle sign in (clock in)
async function handleSignIn() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.attendance_api.clock_in', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token
            }
        });
        const data = await response.json();

        if (data.message && data.message.success) {
            frappe.show_alert({
                message: 'Signed in successfully!',
                indicator: 'green'
            }, 5);

            // Reload data
            checkCheckinStatus();
            loadAttendanceData();
        } else if (data.message && data.message.error) {
            frappe.show_alert({
                message: data.message.error,
                indicator: 'red'
            }, 5);
        }
    } catch (error) {
        console.error('Error signing in:', error);
        frappe.show_alert({
            message: 'Error signing in. Please try again.',
            indicator: 'red'
        }, 5);
    }
}

// Handle sign out (clock out)
async function handleSignOut() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.attendance_api.clock_out', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token
            }
        });
        const data = await response.json();

        if (data.message && data.message.success) {
            frappe.show_alert({
                message: 'Signed out successfully!',
                indicator: 'green'
            }, 5);

            // Reload data
            checkCheckinStatus();
            loadAttendanceData();
        } else if (data.message && data.message.error) {
            frappe.show_alert({
                message: data.message.error,
                indicator: 'red'
            }, 5);
        }
    } catch (error) {
        console.error('Error signing out:', error);
        frappe.show_alert({
            message: 'Error signing out. Please try again.',
            indicator: 'red'
        }, 5);
    }
}

// Download payslip
async function handleDownloadPayslip() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.payroll_api.download_payslip');
        const data = await response.json();

        if (data.message && data.message.pdf_data) {
            // Convert base64 to blob and download
            const pdfData = atob(data.message.pdf_data);
            const pdfArray = new Uint8Array(pdfData.length);
            for (let i = 0; i < pdfData.length; i++) {
                pdfArray[i] = pdfData.charCodeAt(i);
            }
            const blob = new Blob([pdfArray], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);

            // Create temporary link and trigger download
            const a = document.createElement('a');
            a.href = url;
            a.download = data.message.file_name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            frappe.show_alert({
                message: 'Payslip downloaded!',
                indicator: 'green'
            }, 3);
        } else if (data.message && data.message.error) {
            frappe.show_alert({
                message: data.message.error,
                indicator: 'orange'
            }, 5);
        }
    } catch (error) {
        console.error('Error downloading payslip:', error);
        frappe.show_alert({
            message: 'Error downloading payslip. Please try again.',
            indicator: 'red'
        }, 5);
    }
}

// Show/hide salary values
function handleShowSalary() {
    const values = document.querySelectorAll('.breakdown-row .value');
    const showBtn = document.querySelector('.btn-show-salary');

    if (!showBtn) return;

    // Check if currently hidden by looking at the button text or data attribute
    const isHidden = showBtn.textContent.trim() === 'Show Salary';

    if (isHidden) {
        // Show actual values - check if data is already loaded
        const hasData = values[0] && values[0].dataset.value;

        if (hasData) {
            // Data already loaded, just reveal it
            values.forEach(value => {
                if (value.dataset.value) {
                    value.textContent = `₹${Math.round(parseFloat(value.dataset.value)).toLocaleString()}`;
                }
            });
            showBtn.textContent = 'Hide Salary';
        } else {
            // Load data first, then reveal
            loadPayslipData().then(() => {
                showBtn.textContent = 'Hide Salary';
            });
        }
    } else {
        // Hide values - show asterisks
        values.forEach(value => {
            value.textContent = '*****';
        });
        showBtn.textContent = 'Show Salary';
    }
}

// Set up event listeners
function setupEventListeners() {
    // Sign in/out button - handles both actions based on current state
    const signOutBtn = document.querySelector('.btn-sign-out');
    if (signOutBtn) {
        signOutBtn.addEventListener('click', function () {
            const action = this.dataset.action;
            if (action === 'signin') {
                handleSignIn();
            } else if (action === 'signout') {
                handleSignOut();
            }
        });
    }

    // View swipes button - could show history
    const viewSwipesBtn = document.querySelector('.btn-view-swipes');
    if (viewSwipesBtn) {
        viewSwipesBtn.addEventListener('click', () => {
            // Could open a modal with attendance history
            frappe.msgprint({
                title: 'Attendance History',
                message: 'Loading attendance history...',
                indicator: 'blue'
            });
        });
    }

    // Download payslip button
    const downloadBtn = document.querySelector('.btn-download');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', handleDownloadPayslip);
    }

    // Show salary button
    const showSalaryBtn = document.querySelector('.btn-show-salary');
    if (showSalaryBtn) {
        showSalaryBtn.addEventListener('click', handleShowSalary);
    }
}

// Load Pending Reviews for Reporting Manager
function loadPendingReviews() {
    frappe.call({
        method: 'hrms_dashboard.api.review_api.get_pending_reviews',
        callback: function (r) {
            if (r.message && r.message.success) {
                updateReviewWidget(r.message.pending_items, r.message.total_count);
            } else {
                console.log('Pending reviews:', r.message?.message || 'No pending items');
                updateReviewWidget([], 0);
            }
        }
    });
}

// Update Review Widget with pending items
function updateReviewWidget(pendingItems, totalCount) {
    const reviewWidget = document.querySelector('.review-widget .widget-content');
    if (!reviewWidget) return;

    if (!pendingItems || pendingItems.length === 0) {
        // Show empty state
        reviewWidget.innerHTML = `
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='20' y='10' width='60' height='80' fill='%23e3f2fd' stroke='%232196F3' stroke-width='2' rx='5'/%3E%3Cline x1='30' y1='30' x2='70' y2='30' stroke='%232196F3' stroke-width='2'/%3E%3Cline x1='30' y1='45' x2='70' y2='45' stroke='%232196F3' stroke-width='2'/%3E%3Cline x1='30' y1='60' x2='70' y2='60' stroke='%232196F3' stroke-width='2'/%3E%3C/svg%3E"
                alt="Review" class="widget-icon">
            <p class="widget-message">Hurrah! You've nothing to review.</p>
        `;
        return;
    }

    // Group items by employee
    const itemsByEmployee = {};
    pendingItems.forEach(item => {
        if (!itemsByEmployee[item.employee]) {
            itemsByEmployee[item.employee] = {
                employee_name: item.employee_name,
                initials: item.initials,
                items: []
            };
        }
        itemsByEmployee[item.employee].items.push(item);
    });

    // Build HTML with employee initials
    let html = '<div class="review-items-container">';

    // Show count
    html += `<div class="review-count">${totalCount} item(s) pending review</div>`;

    // Show employee initials
    html += '<div class="review-initials-container">';
    Object.keys(itemsByEmployee).forEach(employeeId => {
        const empData = itemsByEmployee[employeeId];
        const itemCount = empData.items.length;

        html += `
            <div class="review-employee-group">
                <span class="review-initial-badge" 
                      data-employee="${employeeId}" 
                      data-items='${JSON.stringify(empData.items)}'
                      title="${empData.employee_name} (${itemCount} item(s))">
                    ${empData.initials}
                </span>
                <span class="review-item-count">${itemCount}</span>
            </div>
        `;
    });
    html += '</div>';
    html += '</div>';

    reviewWidget.innerHTML = html;

    // Add click handlers to initials
    document.querySelectorAll('.review-initial-badge').forEach(badge => {
        badge.addEventListener('click', function () {
            const items = JSON.parse(this.dataset.items);
            showReviewItemsDialog(items);
        });
    });
}

// Show dialog with pending items for an employee
function showReviewItemsDialog(items) {
    if (!items || items.length === 0) return;

    const employeeName = items[0].employee_name;

    let html = '<div class="review-items-list">';
    items.forEach(item => {
        html += `
            <div class="review-item" onclick="window.location.href='/app/${item.doctype.toLowerCase().replace(/ /g, '-')}/${item.name}'">
                <div class="review-item-header">
                    <strong>${item.doctype}</strong>
                    <span class="review-item-date">${item.from_date}</span>
                </div>
                <div class="review-item-description">${item.description}</div>
                <div class="review-item-link">Click to review →</div>
            </div>
        `;
    });
    html += '</div>';

    frappe.msgprint({
        title: `Pending Reviews - ${employeeName}`,
        message: html,
        wide: true
    });
}

// Initialize dashboard
function initDashboard() {
    console.log('Initializing HRMS Dashboard with ERPNext integration...');

    // Start timer and update date
    startTimer();
    updateClockDate();

    // Check if frappe is available (running in ERPNext context)
    if (typeof frappe !== 'undefined') {
        // Load real data from ERPNext
        loadLeaveBalances();  // Load leave balance cards
        loadPendingReviews();  // Load pending reviews
        checkCheckinStatus();
        loadAttendanceData();
        loadLeaveData();
        loadUpcomingHolidays();  // Load upcoming holidays
        // Don't auto-load payslip (keep hidden by default)

        // Set up event listeners
        setupEventListeners();

        // Initialize Greeting and Quote
        updateGreetingAndQuote();

        // Refresh data every 5 minutes
        setInterval(() => {
            loadLeaveBalances();
            loadPendingReviews();
            checkCheckinStatus();
            loadAttendanceData();
            loadLeaveData();
            loadUpcomingHolidays();
        }, 5 * 60 * 1000);

        console.log('HRMS Dashboard initialized with ERPNext integration!');
    } else {
        console.warn('Frappe not available - running in standalone mode');
    }
}

// Export initDashboard to global scope so it can be called from hrms.js
window.initDashboard = initDashboard;
// Load Team Leave Data
function loadLeaveData() {
    frappe.call({
        method: 'hrms_dashboard.api.team_leave_api.get_reporting_team_on_leave',
        callback: function (r) {
            if (r.message && r.message.success) {
                updateTeamLeaveWidget(r.message.team_on_leave);
            } else {
                console.log('Team leave:', r.message?.message || 'No team members on leave');
                // Show empty state
                updateTeamLeaveWidget([]);
            }
        }
    });
}

// Update Team On Leave Widget
function updateTeamLeaveWidget(teamOnLeave) {
    const leaveWidget = document.querySelector('.leave-widget .widget-content');
    if (!leaveWidget) return;

    if (!teamOnLeave || teamOnLeave.length === 0) {
        leaveWidget.innerHTML = `
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='30' cy='30' r='15' fill='%23ffc107'/%3E%3Cpath d='M 30 45 Q 20 55, 30 65 T 50 65' stroke='%23ffc107' fill='none' stroke-width='3'/%3E%3Cpath d='M 50 50 L 70 30 L 80 40 L 60 60 Z' fill='%2332CD32'/%3E%3C/svg%3E"
                alt="Leave" class="widget-icon">
            <p class="widget-message">It's empty here! No one in your team is on leave.</p>
        `;
        return;
    }

    let html = '<div class="team-leave-list">';

    teamOnLeave.forEach(leave => {
        const fromDate = new Date(leave.from_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const toDate = new Date(leave.to_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const dateRange = leave.from_date === leave.to_date ? fromDate : `${fromDate} - ${toDate}`;

        html += `
            <div class="leave-item">
                <div class="leave-employee-initial">
                    <span class="initial-badge-leave" title="${leave.employee_name}">${leave.initials}</span>
                </div>
                <div class="leave-info">
                    <div class="leave-type">${leave.leave_type}</div>
                    <div class="leave-dates">${dateRange}</div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    leaveWidget.innerHTML = html;
}
// Load Upcoming Holidays
function loadUpcomingHolidays() {
    frappe.call({
        method: 'hrms_dashboard.api.holiday_api.get_upcoming_holidays',
        callback: function (r) {
            if (r.message && r.message.success) {
                updateHolidaysWidget(r.message.holidays);
            } else {
                console.log('Holidays:', r.message?.message || 'No holidays found');
                updateHolidaysWidget([]);
            }
        }
    });
}

// Update Upcoming Holidays Widget
function updateHolidaysWidget(holidays) {
    const holidaysWidget = document.querySelector('.holidays-widget .widget-content');
    if (!holidaysWidget) return;

    if (!holidays || holidays.length === 0) {
        holidaysWidget.innerHTML = `
            <p class="widget-message">No upcoming holidays found.</p>
        `;
        return;
    }

    // Store all holidays in a data attribute
    holidaysWidget.setAttribute('data-all-holidays', JSON.stringify(holidays));

    // Initial display: show only first 4 holidays
    renderHolidays(holidays.slice(0, 4), holidaysWidget, holidays.length > 4);
}

// Render holidays with expand/collapse functionality
function renderHolidays(holidaysToShow, container, hasMore) {
    let html = '<div class="holidays-list">';

    holidaysToShow.forEach(holiday => {
        html += `
            <div class="holiday-item">
                <div class="holiday-date-info">
                    <div class="holiday-date">${holiday.day}</div>
                    <div class="holiday-weekday">${holiday.weekday}</div>
                </div>
                <div class="holiday-details">
                    <div class="holiday-name">${holiday.description}</div>
                </div>
                ${holiday.is_optional ? `<button class="btn-apply-holiday" data-date="${holiday.date}">Apply</button>` : ''}
            </div>
        `;
    });

    html += '</div>';

    // Add Show All/Show Less button if there are more holidays
    if (hasMore || holidaysToShow.length > 4) {
        const allHolidays = JSON.parse(container.getAttribute('data-all-holidays') || '[]');
        const isExpanded = holidaysToShow.length > 4;

        html += `
            <div class="holiday-footer">
                <button class="btn-show-all-holidays" onclick="toggleHolidays(${!isExpanded})">
                    ${isExpanded ? 'Show Less' : `Show All (${allHolidays.length})`}
                </button>
            </div>
        `;
    }

    container.innerHTML = html;

    // Add event listeners to Apply buttons (only for optional holidays)
    document.querySelectorAll('.btn-apply-holiday').forEach(btn => {
        btn.addEventListener('click', function () {
            const date = this.dataset.date;
            applyForHoliday(date);
        });
    });
}

// Toggle between showing all holidays and showing limited holidays
function toggleHolidays(showAll) {
    const holidaysWidget = document.querySelector('.holidays-widget .widget-content');
    if (!holidaysWidget) return;

    const allHolidays = JSON.parse(holidaysWidget.getAttribute('data-all-holidays') || '[]');

    if (showAll) {
        renderHolidays(allHolidays, holidaysWidget, false);
    } else {
        renderHolidays(allHolidays.slice(0, 4), holidaysWidget, true);
    }
}

// Apply for Holiday (Optional Holiday)
function applyForHoliday(date) {
    frappe.msgprint({
        title: 'Apply for Optional Holiday',
        message: `Do you want to apply for optional holiday on ${frappe.datetime.str_to_user(date)}?`,
        primary_action: {
            label: 'Apply',
            action: function () {
                // Redirect to leave application form with pre-filled date
                window.location.href = `/app/leave-application/new?from_date=${date}&to_date=${date}`;
            }
        }
    });
}



// Daily Quotes Database
const dailyQuotes = [
    { text: "Life is 10% what happens to us and 90% how we react to it.", author: "Dennis P. Kimbro" },
    { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
    { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
    { text: "Believe you can and you're halfway there.", author: "Theodore Roosevelt" },
    { text: "The future belongs to those who believe in the beauty of their dreams.", author: "Eleanor Roosevelt" },
    { text: "It does not matter how slowly you go as long as you do not stop.", author: "Confucius" },
    { text: "Everything you've ever wanted is on the other side of fear.", author: "George Addair" },
    { text: "Success is not how high you have climbed, but how you make a positive difference to the world.", author: "Roy T. Bennett" },
    { text: "Don't watch the clock; do what it does. Keep going.", author: "Sam Levenson" },
    { text: "The only impossible journey is the one you never begin.", author: "Tony Robbins" }
];

function updateGreetingAndQuote() {
    // Set Greeting
    const hour = new Date().getHours();
    let greeting = "Good Morning";

    if (hour >= 12 && hour < 17) {
        greeting = "Good Afternoon";
    } else if (hour >= 17 && hour < 21) {
        greeting = "Good Evening";
    } else if (hour >= 21 || hour < 4) {
        greeting = "Good Night"; // As requested
    }

    const greetingElement = document.getElementById('greeting-text');
    if (greetingElement) {
        greetingElement.textContent = greeting;
    }

    // Set Daily Quote
    const today = new Date();
    const start = new Date(today.getFullYear(), 0, 0);
    const diff = today - start;
    const oneDay = 1000 * 60 * 60 * 24;
    const dayOfYear = Math.floor(diff / oneDay);

    const quoteIndex = dayOfYear % dailyQuotes.length;
    const quote = dailyQuotes[quoteIndex];

    const quoteText = document.getElementById('quote-text');
    const quoteAuthor = document.getElementById('quote-author');

    if (quoteText && quoteAuthor) {
        quoteText.textContent = quote.text;
        quoteAuthor.textContent = `- ${quote.author}`;
    }
}
