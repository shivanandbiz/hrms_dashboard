// Load Team Attendance (Who is in?)
function loadTeamAttendance() {
    frappe.call({
        method: 'hrms_dashboard.api.team_attendance_api.get_team_attendance_status',
        callback: function (r) {
            if (r.message && r.message.success) {
                updateTeamAttendanceWidget(r.message);
            } else {
                console.log('Team attendance:', r.message?.message || 'No reporting employees');
            }
        }
    });
}

// Update Team Attendance Widget
function updateTeamAttendanceWidget(data) {
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
    if (data.total_team === 0) {
        html += '<p class="attendance-message">We couldn\'t find your team around</p>';
    } else {
        html += `<p class="attendance-message">${data.total_team} team member(s) tracked today</p>`;

    }

    attendanceWidget.innerHTML = html;
}

// Load Attendance Data (legacy function - keeping for compatibility)
function loadAttendanceData() {
    // This function is replaced by loadTeamAttendance
    loadTeamAttendance();
}
