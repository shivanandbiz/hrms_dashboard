"""
Quick SQL queries to verify Employee and Checkin data
Run these in ERPNext > Developer > Query Report or MariaDB console
"""

-- 1. Check reporting relationships
-- This shows which employees report to whom
SELECT 
    e.name as employee_id,
    e.employee_name,
    e.reports_to,
    r.employee_name as reports_to_name,
    e.status,
    e.user_id
FROM `tabEmployee` e
LEFT JOIN `tabEmployee` r ON e.reports_to = r.name
WHERE e.status = 'Active'
ORDER BY e.reports_to;

-- 2. Check today's check-ins
-- This shows all check-ins for today
SELECT 
    ec.employee,
    e.employee_name,
    ec.log_type,
    ec.time,
    DATE(ec.time) as checkin_date
FROM `tabEmployee Checkin` ec
JOIN `tabEmployee` e ON ec.employee = e.name
WHERE DATE(ec.time) = CURDATE()
ORDER BY ec.time DESC;

-- 3. Check specific manager's team check-ins
-- Replace 'your.email@domain.com' with the manager's email
SELECT 
    e.name as employee_id,
    e.employee_name,
    e.reports_to,
    ec.log_type,
    ec.time as checkin_time,
    CASE 
        WHEN ec.time IS NULL THEN 'Not Yet In'
        ELSE 'Checked In'
    END as status
FROM `tabEmployee` e
LEFT JOIN `tabEmployee Checkin` ec ON (
    e.name = ec.employee 
    AND ec.log_type = 'IN' 
    AND DATE(ec.time) = CURDATE()
)
WHERE e.reports_to = (
    SELECT name FROM `tabEmployee` WHERE user_id = 'your.email@domain.com'
)
AND e.status = 'Active';

-- 4. Get initials for all employees
SELECT 
    name,
    employee_name,
    CONCAT(
        UPPER(SUBSTRING_INDEX(employee_name, ' ', 1)),
        UPPER(SUBSTRING(SUBSTRING_INDEX(employee_name, ' ', -1), 1, 1))
    ) as initials
FROM `tabEmployee`
WHERE status = 'Active';
