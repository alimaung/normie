# Views Package Refactoring

This directory contains the refactored views from the original monolithic `views.py` file. The views have been organized into logical modules for better maintainability and organization.

## Module Structure

### `__init__.py`
- Main entry point that imports all view functions
- Maintains backward compatibility with existing URLs and imports

### `core.py` - Core/Public Views
- `home()` - Home page
- `about()` - About page with team information
- `contact()` - Contact page with form submission
- `features_detail()` - Features and capabilities page
- `solutions_*()` - Solution pages (norm, chemicals, spec, directory, tkz)
- `under_construction()` - Under construction placeholder
- `open_request()` - Public request form (accessible to all users)

### `auth.py` - Authentication Views
- `login_view()` - User login with remember me functionality
- `signup_view()` - User registration
- `logout_view()` - User logout
- `profile()` - User profile display
- `notifications()` - User notifications
- `settings()` - User settings
- `user_management()` - Admin user management
- `user_profile_view()` - Enhanced profile view with session info

### `pdf.py` - PDF Processing Views
- `pdf_parser()` - PDF parser hub page
- `pdf_upload()` - Handle PDF file uploads
- `pdf_editor()` - PDF form editor interface
- `pdf_save()` - Save PDF form changes
- `pdf_download()` - Download processed PDF with custom naming
- `pdf_debug()` - Debug PDF form data

### `applicant.py` - Applicant Data Processing
- `applicant_state_parser()` - Applicant data parser hub
- `applicant_upload()` - Handle applicant data file uploads
- `applicant_editor()` - Edit applicant data
- `applicant_save()` - Save applicant data
- `applicant_download()` - Export applicant data as JSON

### `directory.py` - Directory & ChemScan Views
- `directory()` - Directory listing page
- `directory_detail()` - Detailed directory item view
- `chemscan()` - ChemScan analysis dashboard
- `requests_page()` - Requests management page

### `prototyping.py` - Demo/Prototype Views
- `standards()` - Standards management demo
- `requests()` - Material requests demo
- `materials()` - Materials catalog demo
- `releases()` - Release management demo
- `approvals()` - Approval workflows demo (manager/admin only)
- `inventory()` - Inventory management demo
- `reports()` - Reports and analytics demo
- `audit()` - Audit trail demo

### `cmsr.py` - CMSR Workflow Views
- `cmsr_request()` - Create new CMSR request
- `cmsr_detail()` - CMSR request detail with workflow
- `cmsr_list()` - List CMSR requests with filtering
- `cmsr_edit()` - Edit CMSR request
- `cmsr_documents()` - Manage CMSR documents
- `cmsr_chemscan()` - ChemScan assessment
- `cmsr_environmental()` - Environmental assessment
- `cmsr_manufacturing()` - Manufacturing lab approval
- `cmsr_standards()` - Standards office approval

### `inbox.py` - Email/Outlook Integration
- `inbox()` - Email inbox with filtering and search
- `inbox_view_message()` - View individual email
- `inbox_compose()` - Compose new email
- `inbox_reply()` - Reply to email
- `inbox_forward()` - Forward email
- `inbox_delete_message()` - Delete single email
- `inbox_delete()` - Delete multiple emails
- `inbox_categorize_message()` - Categorize single email
- `inbox_categorize()` - Categorize multiple emails

### `ajax.py` - AJAX/API Endpoints
- `check_username_availability()` - Validate username availability
- `check_email_availability()` - Validate email availability

### `utils.py` - Utility Functions
- `filter_applicant_fields()` - Filter and sort applicant form fields
- `parse_spreadsheet_applicant_data()` - Parse CSV/Excel files
- `parse_json_applicant_data()` - Parse JSON files
- `get_next_possible_statuses()` - Determine CMSR workflow transitions

## Key Benefits

1. **Modularity**: Each module has a clear responsibility
2. **Maintainability**: Easier to find and modify specific functionality
3. **Testability**: Modules can be tested independently
4. **Scalability**: New features can be added to appropriate modules
5. **Backward Compatibility**: Existing URLs and imports continue to work

## Import Structure

The `__init__.py` file uses wildcard imports to maintain compatibility:

```python
from .core import *
from .auth import *
from .pdf import *
# ... etc
```

This means existing code can continue to import views as before:

```python
from normieapp.views import home, login_view, pdf_upload
```

## Decorators Usage

Views maintain their original permission decorators:
- `@restrict_read_only_users` - Requires applicant role or above
- `@admin_required` - Admin only
- `@role_required()` - Specific role requirements
- `@can_view_reports` - Report viewing permissions
- `@can_view_audit_logs` - Audit log permissions

## Dependencies

Each module imports only what it needs:
- Django core modules
- Local decorators from `..decorators`
- Models from `..models` (imported locally to avoid circular imports)
- Services from `..services`
- Utility functions from `.utils`

## Migration Notes

The original `views.py` file can be safely removed after this refactoring, as all functionality has been preserved and organized into the new modular structure. 