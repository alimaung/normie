# Template Organization Structure

## Overview
This document outlines the recommended template folder structure for the normieapp, organized by access levels and functionality based on the role-based access control system.

## Recommended Structure

```
normieapp/templates/normieapp/
├── README.md                           # This file
├── base.html                          # Main base template
├── 
├── public/                            # Public templates (no authentication required)
│   ├── home.html                      # Landing page
│   ├── about.html                     # About page
│   ├── contact.html                   # Contact page
│   ├── features.html                  # Features overview
│   ├── login.html                     # Login page
│   ├── signup.html                    # Registration page
│   ├── under_contruction.html         # Under construction placeholder
│   └── solutions/                     # Solution pages for guests
│       ├── solutions_norm.html
│       ├── solutions_chemicals.html
│       ├── solutions_spec.html
│       ├── solutions_directory.html
│       └── solutions_tkz.html
│
├── authenticated/                     # Templates for all authenticated users
│   ├── open_request.html             # Open request form (accessible to all)
│   ├── profile.html                   # User profile
│   ├── notifications.html             # User notifications
│   └── settings.html                  # User settings
│
├── read_only/                         # Templates specifically for read-only users
│   └── restricted_access.html         # Page explaining read-only limitations
│
├── applicant/                         # Templates for applicant role and above
│   ├── cmsr/                          # CMSR workflow templates
│   │   ├── cmsr_list.html
│   │   ├── cmsr_detail.html
│   │   ├── cmsr_request.html
│   │   ├── cmsr_edit.html
│   │   ├── cmsr_chemscan.html
│   │   ├── cmsr_environmental.html
│   │   ├── cmsr_manufacturing.html
│   │   ├── cmsr_standards.html
│   │   └── cmsr_documents.html
│   └── requests_page.html             # General requests page
│
├── specialist/                        # Templates for specialist roles
│   ├── chemscan.html                  # ChemScan analysis
│   ├── directory.html                 # Material directory
│   ├── directory_detail.html          # Directory details
│   └── applicant_state_parser.html    # Applicant state analysis
│
├── manager/                           # Templates for manager role and above
│   ├── inbox/                         # Email management
│   │   ├── inbox.html
│   │   ├── inbox_view_message.html
│   │   ├── inbox_compose.html
│   │   ├── inbox_reply.html
│   │   └── inbox_forward.html
│   ├── reports.html                   # Reporting dashboard
│   └── user_profile_view.html         # Enhanced user profile management
│
├── admin/                             # Templates for admin-only features
│   ├── pdf_parser.html                # PDF parsing tools
│   ├── pdf_form/                      # PDF form templates
│   │   ├── pdf_form.html
│   │   ├── applicant.html
│   │   ├── chemscan_a.html
│   │   ├── chemscan_b.html
│   │   ├── environmental.html
│   │   ├── manufacturing.html
│   │   ├── standards.html
│   │   └── signature.html
│   ├── user_management.html           # User management
│   ├── audit.html                     # Audit logs
│   └── prototyping/                   # Admin prototyping tools
│       ├── approvals.html
│       ├── audit.html
│       ├── chemical_approval.html
│       ├── inventory.html
│       ├── materials.html
│       ├── releases.html
│       ├── reports.html
│       ├── requests.html
│       └── standards.html
│
├── includes/                          # Reusable template components
│   ├── signature_field.html           # Signature field component
│   ├── message_alert.html             # Alert messages
│   ├── pagination.html                # Pagination component
│   ├── user_badge.html                # User role badge
│   └── navigation/                    # Navigation components
│       ├── main_nav.html
│       ├── admin_nav.html
│       ├── user_menu.html
│       └── breadcrumbs.html
│
└── errors/                            # Error page templates
    ├── 403.html                       # Forbidden (insufficient permissions)
    ├── 404.html                       # Not found
    ├── 500.html                       # Server error
    └── permission_denied.html          # Custom permission denied page
```

## Access Level Mapping

### Public Templates (`public/`)
- **Access**: No authentication required
- **Users**: Guests, all users
- **Purpose**: Marketing, authentication, general information

### Authenticated Templates (`authenticated/`)
- **Access**: `@login_required` or `@read_only_or_above_required`
- **Users**: All authenticated users regardless of role
- **Purpose**: Basic user functionality available to everyone

### Read-only Templates (`read_only/`)
- **Access**: Specifically for read-only users
- **Users**: Users with `role == 'read_only'`
- **Purpose**: Limited functionality with helpful explanations

### Applicant Templates (`applicant/`)
- **Access**: `@restrict_read_only_users` (blocks read-only users)
- **Users**: Applicant role and above
- **Purpose**: Request creation and management

### Specialist Templates (`specialist/`)
- **Access**: Role-specific decorators for specialists
- **Users**: ChemScan specialists, environmental reviewers, etc.
- **Purpose**: Specialized analysis and review tools

### Manager Templates (`manager/`)
- **Access**: `@manager_or_admin_required`
- **Users**: Managers and admins
- **Purpose**: Management and oversight functionality

### Admin Templates (`admin/`)
- **Access**: `@admin_required`
- **Users**: Administrators only
- **Purpose**: System administration and advanced tools

## Implementation Guidelines

### 1. Template Organization
- Keep templates in folders that match their access requirements
- Use descriptive folder names that reflect the minimum role required
- Group related functionality together (e.g., all CMSR templates in `applicant/cmsr/`)

### 2. View Updates
When moving templates, update view functions to reference the new paths:

```python
# Before
return render(request, 'normieapp/user_management.html', context)

# After
return render(request, 'normieapp/admin/user_management.html', context)
```

### 3. Template Inheritance
- All templates should extend `base.html`
- Consider creating role-specific base templates:
  - `public/base_public.html` - No authentication features
  - `admin/base_admin.html` - Admin-specific navigation and tools

### 4. Security Benefits
- **Visual organization**: Easy to see which templates require which permissions
- **Security review**: Easier to audit access controls
- **Maintenance**: Clear structure for adding new features
- **Documentation**: Self-documenting folder structure

### 5. Migration Strategy
1. Create the new folder structure
2. Move templates gradually, starting with clear categories (public, admin)
3. Update view references as you move templates
4. Test each moved template to ensure proper access control
5. Update any hardcoded template references in other templates

## Template Naming Conventions

- Use descriptive names that indicate functionality
- Include the access level in the folder, not the filename
- Use consistent naming patterns within each folder
- Separate words with underscores for better readability

## Benefits of This Structure

1. **Security Clarity**: Immediately obvious which templates require which permissions
2. **Easier Maintenance**: Related functionality grouped together
3. **Better Organization**: Logical hierarchy based on access levels
4. **Scalability**: Easy to add new features in the appropriate access level
5. **Onboarding**: New developers can quickly understand the permission structure
6. **Code Review**: Easier to spot potential security issues during reviews 