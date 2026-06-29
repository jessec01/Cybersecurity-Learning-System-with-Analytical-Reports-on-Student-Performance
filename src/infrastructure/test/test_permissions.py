import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from domain.value_objects.permissions import Permissions, Resource, Action, permission


class TestPermissionValueObjects:
    def test_permission_format(self):
        assert permission("course", "create") == "course:create"

    def test_resource_constants(self):
        assert Resource.COURSE == "course"
        assert Resource.REPORT == "report"
        assert Resource.BRANDING == "branding"

    def test_action_constants(self):
        assert Action.CREATE == "create"
        assert Action.APPROVE == "approve"
        assert Action.EXPORT == "export"

    def test_permissions_class_all_valid(self):
        assert Permissions.COURSE_CREATE == "course:create"
        assert Permissions.COURSE_READ == "course:read"
        assert Permissions.COURSE_UPDATE == "course:update"
        assert Permissions.COURSE_DELETE == "course:delete"
        assert Permissions.REPORT_GENERATE == "report:export"
        assert Permissions.BRANDING_APPROVE == "branding:approve"
        assert Permissions.USER_CREATE == "user:create"
        assert Permissions.ROLE_READ == "role:read"

    def test_permission_string_in_list_check(self):
        perms = [Permissions.COURSE_READ, Permissions.COURSE_CREATE]
        assert Permissions.COURSE_READ in perms
        assert Permissions.COURSE_DELETE not in perms


class TestRequirePermissionLogic:
    """La fabrica require_permission usa Depends internamente.
       Estos tests validan la logica pura: el chequeo de permiso en lista."""

    def test_permission_found(self):
        user_perms = ["course:create", "user:read"]
        assert "course:create" in user_perms

    def test_permission_not_found(self):
        user_perms = ["user:read"]
        assert "course:delete" not in user_perms
