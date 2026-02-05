/**
 * HRMS Dashboard - JavaScript with ERPNext Integration
 * Handles timer, real API calls, and interactive features
 */

// Global state
let timerInterval = null;
let currentEmployee = null;

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

// Load attendance data from ERPNext
async function loadAttendanceData() {
    try {
        const response = await fetch('/api/method/hrms_dashboard.api.attendance_api.get_attendance_status');
        const data = await response.json();

        if (data.message && !data.message.error) {
            updateAttendanceWidget(data.message);
        } else if (data.message && data.message.error) {
            console.error('Attendance error:', data.message.error);
        }
    } catch (error) {
        console.error('Error loading attendance:', error);
    }
}

// Update attendance widget with real data
function updateAttendanceWidget(data) {
    const notYetBadge = document.querySelector('.status-badge.not-yet');
    const lateBadge = document.querySelector('.status-badge.late');
    const onTimeBadge = document.querySelector('.status-badge.on-time');

    if (notYetBadge) {
        notYetBadge.textContent = `Not Yet In (${data.not_yet_in || 0})`;
    }
    if (lateBadge) {
        lateBadge.textContent = `Late Arrivals (${data.late_arrivals || 0})`;
    }
    if (onTimeBadge) {
        onTimeBadge.textContent = `On Time (${data.on_time || 0})`;
    }

    // Update message if team is empty
    const attendanceMessage = document.querySelector('.attendance-widget .attendance-message');
    if (attendanceMessage && data.team_members && data.team_members.length > 0) {
        attendanceMessage.textContent = `${data.team_members.length} team members tracked today`;
    }
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

// Update check-in/out buttons based on status
function updateCheckinButtons(status) {
    const signOutBtn = document.querySelector('.btn-sign-out');
    const viewSwipesBtn = document.querySelector('.btn-view-swipes');

    if (signOutBtn) {
        if (status.checked_in && !status.checked_out) {
            signOutBtn.textContent = 'Sign Out';
            signOutBtn.disabled = false;
            signOutBtn.style.opacity = '1';
        } else if (status.checked_out) {
            signOutBtn.textContent = 'Signed Out';
            signOutBtn.disabled = true;
            signOutBtn.style.opacity = '0.5';
        } else {
            signOutBtn.textContent = 'Sign In First';
            signOutBtn.disabled = true;
            signOutBtn.style.opacity = '0.5';
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
        }
    } catch (error) {
        console.error('Error loading payslip:', error);
    }
}

// Update payslip widget with real data
function updatePayslipWidget(data) {
    if (!data || data.error) return;

    // Update breakdown values
    const grossPay = document.querySelector('.breakdown-item:nth-child(1) .value');
    const deduction = document.querySelector('.breakdown-item:nth-child(2) .value');
    const netPay = document.querySelector('.breakdown-item:nth-child(3) .value');

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
        paidDaysElement.innerHTML = `${data.payment_days}<br>Paid Days`;
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

        if (data.message && data.message.file_url) {
            window.open(data.message.file_url, '_blank');
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
    const values = document.querySelectorAll('.breakdown-item .value');
    const showBtn = document.querySelector('.btn-show-salary');

    if (!showBtn) return;

    const isHidden = values[0] && values[0].textContent === '****';

    if (isHidden) {
        // Load and show actual values
        loadPayslipData();
        showBtn.textContent = 'Hide Salary';
    } else {
        // Hide values
        values.forEach(value => {
            value.textContent = '****';
        });
        showBtn.textContent = 'Show Salary';
    }
}

// Set up event listeners
function setupEventListeners() {
    // Sign out button
    const signOutBtn = document.querySelector('.btn-sign-out');
    if (signOutBtn) {
        signOutBtn.addEventListener('click', handleSignOut);
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

// Initialize dashboard
function initDashboard() {
    console.log('Initializing HRMS Dashboard with ERPNext integration...');

    // Start timer
    startTimer();

    // Check if frappe is available (running in ERPNext context)
    if (typeof frappe !== 'undefined') {
        // Load real data from ERPNext
        checkCheckinStatus();
        loadAttendanceData();
        loadLeaveData();
        // Don't auto-load payslip (keep hidden by default)

        // Set up event listeners
        setupEventListeners();

        // Refresh data every 5 minutes
        setInterval(() => {
            checkCheckinStatus();
            loadAttendanceData();
            loadLeaveData();
        }, 5 * 60 * 1000);

        console.log('HRMS Dashboard initialized with ERPNext integration!');
    } else {
        console.warn('Frappe not available - running in standalone mode');
    }
}

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
