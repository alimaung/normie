"""
View module compatibility layer.
This file imports all views from the views directory to maintain backward compatibility.
After the refactoring, all views are now organized in the views/ directory.
"""

# Import all views using wildcards for simplicity
from .views.core import *
from .views.pdf import *
from .views.applicant import *
from .views.cmsr import *
from .views.directory import *
from .views.prototyping import *
from .views.inbox import *
from .views.ajax import *
from .views.utils import *
from .views.mlc import *

# Import auth views except settings to avoid Django conflict
from .views.auth import (
    login_view, signup_view, logout_view, profile, notifications, 
    user_management, user_profile_view
)

# Import settings with specific handling to avoid Django settings conflict
from .views.auth import settings as settings_view
settings = settings_view 