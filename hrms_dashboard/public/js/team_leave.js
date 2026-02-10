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
                <div class="leave-employee-info">
                    <div class="employee-name">${leave.employee_name}</div>
                    <div class="leave-details">
                        <span class="leave-type-badge">${leave.leave_type}</span>
                        <span class="leave-dates">${dateRange}</span>
                        ${leave.total_days ? `<span class="leave-days">(${leave.total_days} day${leave.total_days > 1 ? 's' : ''})</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    leaveWidget.innerHTML = html;
}
