# HRMS Testing Checklist

## Employee Authentication Tests

### Registration Flow
- [ ] Admin can register new employee
- [ ] Registration generates invitation token
- [ ] Invalid employee_id (without EMP) is rejected
- [ ] Duplicate username is rejected
- [ ] Duplicate employee_id is rejected

### Password Setup
- [ ] Valid token allows password setting
- [ ] Invalid token is rejected
- [ ] Expired token is rejected
- [ ] Password mismatch is rejected
- [ ] Weak password is rejected

### Login
- [ ] Valid credentials return tokens
- [ ] Response includes role information
- [ ] Invalid credentials return 401
- [ ] Inactive account returns 403

### Role-based Access
- [ ] Admin can access register endpoint
- [ ] Employee cannot access register endpoint
- [ ] Employee can access own profile
- [ ] Employee cannot access other profiles (admin endpoints)

---

## Attendance Tests

### Check-In
- [ ] Check-in creates attendance record
- [ ] Check-in sets status to "Working"
- [ ] Check-in records time correctly
- [ ] Double check-in is blocked

### Check-Out
- [ ] Check-out requires prior check-in
- [ ] Check-out calculates working hours
- [ ] Double check-out is blocked

### Status Logic
- [ ] <4 hours → Absent
- [ ] 4-8 hours → Half Day
- [ ] 8+ hours → Present
- [ ] Late if check-in after 9:30 AM

### Reports
- [ ] Today's attendance returns correct data
- [ ] Monthly report includes summary
- [ ] Auto-absent marks no-shows after 12 PM

---

## Payroll Tests

### Status Management
- [ ] Can set status Pending → Paid
- [ ] Cannot set Paid → Paid (blocked)
- [ ] Empty status is rejected
- [ ] Status change is logged

### Logs
- [ ] Status changes create log entries
- [ ] Logs include user who made change
- [ ] Logs can be filtered by employee

### Batch Operations
- [ ] Run payroll creates records for all active employees
- [ ] Duplicate payroll for same month is prevented
- [ ] Net salary calculated correctly

---

## Run Tests
```bash
# Activate environment
source env/bin/activate

# Run all tests
python manage.py test

# Run specific module
python manage.py test employee.tests
python manage.py test attendance.tests
python manage.py test payroll.tests
```

---

## Manual API Testing (Postman)

1. Import `docs/HRMS_Postman_Collection.json`
2. Set `baseUrl` variable to your server
3. Login as admin → save `accessToken`
4. Test each endpoint in order

### Expected Results
| Endpoint | Expected Status |
|----------|----------------|
| POST /login/ | 200 |
| POST /employee/register/ | 201 |
| POST /employee/set-password/ | 200 |
| POST /employee/login/ | 200 |
| POST /attendance/check-in/ | 200 |
| POST /attendance/check-out/ | 200 |
| POST /payroll/set-status/ | 200 |
| GET /dashboard/stats/ | 200 |
