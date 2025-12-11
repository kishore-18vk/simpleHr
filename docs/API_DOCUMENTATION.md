# HRMS System - API Documentation

## Base URL
```
Development: http://localhost:8000/api
Production: https://your-domain.com/api
```

## Authentication
All protected endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### Login (General)
```http
POST /api/login/
```
**Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
**Response:** `{ "access": "token", "refresh": "token" }`

### Employee Login
```http
POST /api/employee/login/
```
**Response includes role information:**
```json
{
  "access": "token",
  "refresh": "token",
  "user": { "id": 1, "username": "john" },
  "employee": { "id": 1, "employee_id": "EMP001", "role": "employee" }
}
```

### Register Employee (Admin only)
```http
POST /api/employee/register/
```
**Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "employee_id": "EMP002",
  "username": "johndoe",
  "email": "john@company.com",
  "phone": "1234567890",
  "gender": "Male",
  "department": "Engineering",
  "designation": "Developer",
  "date_of_joining": "2025-01-01",
  "role": "employee"
}
```
**Response:**
```json
{
  "message": "Employee registered successfully",
  "invitation_token": "token_string",
  "set_password_url": "/api/employee/set-password/?token=..."
}
```

### Set Password (Public)
```http
POST /api/employee/set-password/
```
**Body:**
```json
{
  "token": "invitation_token",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

### My Profile (Authenticated)
```http
GET /api/employee/me/
PUT /api/employee/me/
```

---

## Attendance Endpoints

### Check-In
```http
POST /api/attendance/check-in/
```
**Body:** `{ "employee_id": "EMP001" }` or use auth token

**Response:**
```json
{
  "message": "Check-in successful",
  "check_in_time": "09:00:00",
  "status": "Working"
}
```

### Check-Out
```http
POST /api/attendance/check-out/
```
**Response:**
```json
{
  "message": "Check-out successful",
  "working_hours": "8h 30m",
  "status": "Present"
}
```

### Today's Attendance
```http
GET /api/attendance/today/{employee_id}/
```

### Monthly Report
```http
GET /api/attendance/report/?month=2025-12&employee_id=EMP001
```
**Response:**
```json
{
  "month": "2025-12",
  "summary": { "present": 20, "absent": 2, "half_day": 3, "late": 5 },
  "records": [...]
}
```

### Auto-Absent (Scheduled)
```http
POST /api/attendance/auto-absent/
```
Marks all employees without check-in as Absent (run after 12 PM)

### Daily Stats
```http
GET /api/attendance/stats/?date=2025-12-11
```

---

## Payroll Endpoints

### Set Status (with logging)
```http
POST /api/payroll/set-status/
```
**Body:**
```json
{
  "payroll_id": 1,
  "status": "Paid",
  "notes": "December salary processed"
}
```
**Validations:**
- Cannot set "Paid" twice
- Status cannot be empty

### Get Employee Payroll
```http
GET /api/payroll/employee/{employee_id}/
```

### Get All Payroll
```http
GET /api/payroll/all/?status=Pending&month=12&year=2025
```

### Run Payroll (Batch)
```http
POST /api/payroll/run_payroll/
```
Generates payroll for all active employees for current month

### Mark Paid (Legacy)
```http
POST /api/payroll/{id}/mark_paid/
```

### Status Change Logs
```http
GET /api/payroll/logs/?employee_id=EMP001
```

### Payroll Stats
```http
GET /api/payroll/payroll_stats/
```
Returns total, paid, pending amounts

---

## Dashboard
```http
GET /api/dashboard/stats/
```
Returns comprehensive dashboard data (employees, attendance, payroll, trends)

---

## Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized |
| 403 | Forbidden (role not allowed) |
| 404 | Not Found |
