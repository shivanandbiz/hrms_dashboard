frappe.pages['hrms'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'HRMS Dashboard',
        single_column: true
    });

    // Remove default padding for full-width dashboard
    page.main.css({
        'padding': '0',
        'background': '#f5f7fa'
    });

    // Load the dashboard HTML
    frappe.call({
        method: 'hrms_dashboard.hrms_dashboard.page.hrms.hrms.get_dashboard_html',
        callback: function (r) {
            if (r.message) {
                $(page.main).html(r.message);

                // Load CSS
                if (!$('link[href="/assets/hrms_dashboard/css/hrms_dashboard.css"]').length) {
                    $('<link>')
                        .attr('rel', 'stylesheet')
                        .attr('href', '/assets/hrms_dashboard/css/hrms_dashboard.css')
                        .appendTo('head');
                }

                // Load JS and initialize dashboard after HTML is ready
                $.getScript('/assets/hrms_dashboard/js/hrms_dashboard.js', function () {
                    // Call initDashboard after script loads
                    if (typeof initDashboard === 'function') {
                        initDashboard();
                    }
                });
            }
        }
    });
}
