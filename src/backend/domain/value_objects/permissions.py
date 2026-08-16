from enum import StrEnum


class Resource(str):
    COURSE = "course"
    UNIT = "unit"
    TASK = "task"
    STUDENT = "student"
    REPORT = "report"
    TEACHER = "teacher"
    BRANDING = "branding"
    USER = "user"
    ROLE = "role"
    HELP = "help"


class Action(str):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    APPROVE = "approve"
    REJECT = "reject"


def permission(resource: str, action: str) -> str:
    return f"{resource}:{action}"


class Permissions:
    COURSE_CREATE = permission(Resource.COURSE, Action.CREATE)
    COURSE_READ = permission(Resource.COURSE, Action.READ)
    COURSE_UPDATE = permission(Resource.COURSE, Action.UPDATE)
    COURSE_DELETE = permission(Resource.COURSE, Action.DELETE)

    UNIT_CREATE = permission(Resource.UNIT, Action.CREATE)
    UNIT_READ = permission(Resource.UNIT, Action.READ)
    UNIT_UPDATE = permission(Resource.UNIT, Action.UPDATE)
    UNIT_DELETE = permission(Resource.UNIT, Action.DELETE)

    TASK_CREATE = permission(Resource.TASK, Action.CREATE)
    TASK_READ = permission(Resource.TASK, Action.READ)
    TASK_UPDATE = permission(Resource.TASK, Action.UPDATE)
    TASK_DELETE = permission(Resource.TASK, Action.DELETE)

    STUDENT_READ = permission(Resource.STUDENT, Action.READ)
    STUDENT_UPDATE = permission(Resource.STUDENT, Action.UPDATE)

    REPORT_GENERATE = permission(Resource.REPORT, Action.EXPORT)
    REPORT_READ = permission(Resource.REPORT, Action.READ)

    TEACHER_CREATE = permission(Resource.TEACHER, Action.CREATE)
    TEACHER_READ = permission(Resource.TEACHER, Action.READ)
    TEACHER_UPDATE = permission(Resource.TEACHER, Action.UPDATE)

    BRANDING_APPROVE = permission(Resource.BRANDING, Action.APPROVE)
    BRANDING_REJECT = permission(Resource.BRANDING, Action.REJECT)
    BRANDING_READ = permission(Resource.BRANDING, Action.READ)

    USER_CREATE = permission(Resource.USER, Action.CREATE)
    USER_READ = permission(Resource.USER, Action.READ)
    USER_UPDATE = permission(Resource.USER, Action.UPDATE)
    USER_DELETE = permission(Resource.USER, Action.DELETE)

    ROLE_CREATE = permission(Resource.ROLE, Action.CREATE)
    ROLE_READ = permission(Resource.ROLE, Action.READ)
    ROLE_UPDATE = permission(Resource.ROLE, Action.UPDATE)
