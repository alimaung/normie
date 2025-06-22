# Role-Based Access Control (RBAC) System

This document describes the role-based access control system implemented for the Normie Django application.

## Overview

The system provides fine-grained access control with different user roles and permissions, ensuring that users can only access the features and data they're authorized to use.

## User Roles

### 1. Administrator (`admin`)
- **Full system access**
- Can manage all users and their roles
- Access to all CMSR requests and assessments
- Can view reports and audit logs
- Can perform all assessment types

### 2. Manager (`manager`)
- Can view all CMSR requests
- Can approve requests
- Access to reports and audit logs
- Cannot delete requests or manage users

### 3. ChemScan Specialist (`chemscan_specialist`)
- Can perform ChemScan assessments
- Can view all requests
- Limited to ChemScan-related functions

### 4. Environmental Reviewer (`environmental_reviewer`)
- Can perform environmental assessments
- Can view all requests
- Limited to environmental review functions

### 5. Manufacturing Reviewer (`manufacturing_reviewer`)
- Can perform manufacturing lab assessments
- Can view all requests
- Limited to manufacturing review functions

### 6. Standards Officer (`standards_officer`)
- Can perform final standards approval
- Can approve requests
- Can view all requests

### 7. Read Only (`read_only`)
- Can view all requests and information
- Cannot create, edit, or delete anything
- View-only access to the system

### 8. Applicant (`applicant`)
- Can create and edit their own requests
- Can only view their own requests
- Basic user role for request submission

## Permission System

Each role has specific permissions that are automatically set when the role is assigned:

- `can_create_requests`: Create new CMSR requests
- `can_edit_requests`: Edit existing requests
- `can_delete_requests`: Delete requests
- `can_approve_requests`: Approve or reject requests
- `can_perform_chemscan`: Perform ChemScan assessments
- `can_environmental_review`: Perform environmental reviews
- `can_manufacturing_review`: Perform manufacturing reviews
- `can_standards_review`: Perform standards office reviews
- `can_view_all_requests`: View all requests in the system
- `can_manage_users`: Manage user accounts and roles
- `can_view_reports`: Access reports and analytics
- `can_view_audit_logs`: View system audit logs

## Implementation Details

### Models
- `UserProfile`: Extends the Django User model with role and permission fields
- Automatic profile creation via Django signals

### Decorators
- `@role_required('role1', 'role2')`: Restrict view to specific roles
- `@permission_required('permission_name')`: Require specific permission
- `@admin_required`: Admin-only access
- `@manager_or_admin_required`: Manager or admin access
- `@can_view_reports`: Report viewing permission
- `@can_view_audit_logs`: Audit log viewing permission

### Helper Functions
- `user_can_access_request(user, cmsr_request)`: Check if user can access a specific request
- `user_can_edit_request(user, cmsr_request)`: Check if user can edit a specific request

## Usage Examples

### Protecting Views
```python
from .decorators import role_required, permission_required

@role_required('admin', 'manager')
def sensitive_view(request):
    # Only admins and managers can access this view
    pass

@permission_required('can_view_reports')
def reports_view(request):
    # Only users with report viewing permission can access
    pass
```

### Checking Permissions in Templates
```html
{% if user.profile.can_create_requests %}
    <a href="{% url 'create_request' %}">Create Request</a>
{% endif %}
```

### Checking Access in Views
```python
if not user_can_access_request(request.user, cmsr_request):
    return redirect('access_denied')
```

## Admin Interface

### User Management
- Access via `/users/` (admin only)
- Change user roles through web interface
- View user permissions and details

### Django Admin
- Enhanced user admin with profile information
- Bulk user management capabilities
- Permission overview

## Getting Started

### 1. Create Admin User
```bash
python manage.py create_admin
# Creates admin user with username: admin, password: admin123
```

### 2. Custom Admin User
```bash
python manage.py create_admin --username myuser --email user@example.com --password mypassword
```

### 3. Assign Roles
- Log in as admin
- Go to `/users/` to manage user roles
- Or use Django admin at `/admin/`

## Security Features

1. **Automatic Permission Assignment**: Permissions are automatically set based on role
2. **Request-Level Access Control**: Users can only access requests they're authorized to see
3. **Status-Based Editing**: Users can only edit requests in appropriate workflow stages
4. **Template-Level Security**: UI elements are hidden based on permissions
5. **Signal-Based Profile Creation**: User profiles are automatically created

## URLs

- `/users/` - User management (admin only)
- `/my-profile/` - View own profile and permissions
- `/admin/` - Django admin interface

## Migration

The system includes database migrations for the UserProfile model. Run:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### User Has No Profile
If a user doesn't have a profile, it will be automatically created when they log in or when accessed through the system.

### Permission Denied Errors
Check that:
1. User has the correct role assigned
2. Role has the required permissions
3. View is properly decorated with access control decorators

### Role Changes Not Taking Effect
Role changes take effect immediately. If issues persist:
1. Check that the user's profile was properly updated
2. Ensure the user logs out and back in
3. Verify the role permissions are correctly set

## Customization

To add new roles or permissions:
1. Update `ROLE_CHOICES` in `models.py`
2. Add permission fields to `UserProfile` model
3. Update the `save()` method to set permissions for new roles
4. Create and run migrations
5. Update decorators and helper functions as needed 