// Load Upcoming Holidays
function loadUpcomingHolidays() {
    frappe.call({
        method: 'hrms_dashboard.api.holiday_api.get_upcoming_holidays',
        args: {
            limit: 5
        },
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

    let html = '<div class="holidays-list">';

    holidays.forEach(holiday => {
        html += `
            <div class="holiday-item">
                <div class="holiday-date-info">
                    <div class="holiday-date">${holiday.day}</div>
                    <div class="holiday-weekday">${holiday.weekday}</div>
                </div>
                <div class="holiday-details">
                    <div class="holiday-name">${holiday.description}</div>
                </div>
                <button class="btn-apply-holiday" data-date="${holiday.date}">Apply</button>
            </div>
        `;
    });

    html += '</div>';
    holidaysWidget.innerHTML = html;

    // Add event listeners to Apply buttons
    document.querySelectorAll('.btn-apply-holiday').forEach(btn => {
        btn.addEventListener('click', function () {
            const date = this.dataset.date;
            applyForHoliday(date);
        });
    });
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
