import os
from datetime import date
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()
date=date.today()
KEYUNIT='units.id_unit'
VARCHARMEDIUM='VARCHAR(200)'
VARCHARLARGE='VARCHAR(500)'
TODAY='NOW()'
KEYPERSON='persons.id_person'
kEYSTUDENT='students.id_student'
KEYCOURSE='courses.id_course'
KEYCOURSEREGITRATION='course_registration.id_course_registration'
metadata={
"contract_name": "cybersecurity_learning_system",
"version": "1.0.0",
"created_at": date,
"last_updated": date,

"_doc": "GOLDEN RULES - If you break this, you break the contract"
}
rules={
    "allow_new_tables": False,
    "allow_delete_tables": False,
    "allow_new_columns": True,
    "allow_delete_columns": False,
    "allow_rename_columns": False,
    "allow_rename_tables": False
}
databases={
    "backend": {
    "name": os.getenv("POSTGRES_DB"),
    "owner": "backend team",
    "role": "source_of_truth",
    "allowed_operations": ["INSERT", "UPDATE", "SELECT", "ALTER_TABLE_ADD_COLUMN"]
    },
    "data_engineering": {
      "name": os.getenv("ANALYTICS_DB"),
      "owner": "data_engineering team",
      "role": "read_only_db",
      "allowed_operations": ["SELECT"],
    }
}
tables={
  #tabla que almacena los roles de los usuarios
    "roles": {
      "primary_key": "id_roles",
      "columns": {
        "id_roles":          { "type": "INT", "nullable": False },
        "name":              { "type": "VARCHAR(70)", "nullable": False,"unique": True },
        "is_active":         { "type": "BOOLEAN", "default": False, "nullable": False},
        "created_at":        { "type": "TIMESTAMP", "nullable": True, "default": TODAY },
        "updated_at":        { "type": "TIMESTAMP", "nullable": True }
      },
      "sync_strategy": "full_refresh",
      "notes": "Tabla maestra de roles"
    },
  #tabla que almacena los usuarios
  "users": {
      "primary_key": "id_user",
      "columns": {
        "id_user":             { "type": "INT", "nullable": False },
        "username":            { "type": VARCHARMEDIUM, "nullable": False,"unique": True },
        "password":            { "type": VARCHARLARGE, "nullable": False},
        "is_email_verified":   { "type": "BOOLEAN", "default": False, "nullable": False},
        "is_token_verified":   { "type": "BOOLEAN", "default": False, "nullable": False},
        "is_token_reset":      { "type": "BOOLEAN", "default": False, "nullable": False},
        "is_token_expired":    { "type": "BOOLEAN", "default": False, "nullable": False},
        "is_active":           { "type": "BOOLEAN", "default": False, "nullable": False},
        "created_at":          { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
        "updated_at":          { "type": "TIMESTAMP", "nullable": True }
      },
      "sync_strategy": "full_refresh",
      "notes": "Tabla maestra de usuarios"
    },
  #tabla que almacena las personas"
  "persons": {
      "primary_key": "id_person",
      "columns": {
        "id_person":       { "type": "INT", "nullable": False },
        "first_name":      { "type": VARCHARMEDIUM, "nullable": False,"unique": True, "index": True},
        "last_name":       { "type": VARCHARMEDIUM, "nullable": False, "index": True},
        "mail":            { "type": VARCHARLARGE, "nullable": False,"unique": True },
        "phone":           { "type": "VARCHAR(20)", "nullable": True,"unique": True },
        "date_of_birth":   { "type": "DATE", "nullable": True },
        "id_users":         { "type": "INT", "nullable": False, "fk": "users.id_user" }
      },
      "foreign_keys": {
        "id_users": {"references": "users.id_user", "on_delete": "CASCADE"}
      },
      "sync_strategy": "full_refresh",
      "notes": "Tabla maestra de personas"
    },
  #tabla que almacena la relacion entre personas y roles
    "rol_persons": {
      "primary_key": ["id_person", "id_rol"],
      "columns": {
        "id_person":   { "type": "INT", "nullable": False, "fk": KEYPERSON },
        "id_rol":      { "type": "INT", "nullable": False, "fk": "roles.id_roles" },
        "is_active":   { "type": "BOOLEAN", "default": False, "nullable": False},
        "created_at":  { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
        "updated_at":  { "type": "TIMESTAMP", "nullable": True }
      },
      "foreign_keys": {
        "id_person": {"references": KEYPERSON, "on_delete": "CASCADE"},
        "id_rol":    {"references": "roles.id_roles",    "on_delete": "CASCADE"}
      },
      "sync_strategy": "full_refresh",
      "notes": "Relacion mucho a muchas entre personas y roles"
    },
  #tabla que almacena los permisos del sistema (resource + action)
    "permissions": {
      "primary_key": "id_permission",
      "columns": {
        "id_permission": { "type": "INT", "nullable": False },
        "codename":      { "type": "VARCHAR(100)", "nullable": False, "unique": True },
        "resource":      { "type": "VARCHAR(70)", "nullable": False, "index": True },
        "action":        { "type": "VARCHAR(50)", "nullable": False },
        "description":   { "type": "TEXT", "nullable": False },
        "is_active":     { "type": "BOOLEAN", "default": True, "nullable": False },
        "created_at":    { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
        "updated_at":    { "type": "TIMESTAMP", "nullable": True }
      },
      "sync_strategy": "full_refresh",
      "notes": "Tabla maestra de permisos. resource = dominio, action = verbo permitido"
    },
  #tabla que asigna permisos a roles (muchos a muchos)
    "rol_permissions": {
      "primary_key": ["id_rol", "id_permission"],
      "columns": {
        "id_rol":         { "type": "INT", "nullable": False, "fk": "roles.id_roles" },
        "id_permission":  { "type": "INT", "nullable": False, "fk": "permissions.id_permission" },
        "is_active":      { "type": "BOOLEAN", "default": True, "nullable": False },
        "created_at":     { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
        "updated_at":     { "type": "TIMESTAMP", "nullable": True }
      },
      "foreign_keys": {
        "id_rol":         { "references": "roles.id_roles", "on_delete": "CASCADE" },
        "id_permission":  { "references": "permissions.id_permission", "on_delete": "CASCADE" }
      },
      "sync_strategy": "full_refresh",
      "notes": "Relacion muchos a muchos entre roles y permisos"
    },
  #tabla que almacena los super admin
    "super_admins": {
      "primary_key": ["id_super_admin"],
      "columns": {
        "id_super_admin":           { "type": "INT", "nullable": False },
        "secret_key":               { "type": VARCHARLARGE, "nullable": False,"unique": True },
        "id_person":                { "type": "INT", "nullable": False, "fk": KEYPERSON },
        "created_at":               { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
        "updated_at":               { "type": "TIMESTAMP", "nullable": True }
      },
      "foreign_keys": {
        "id_person": {"references": KEYPERSON, "on_delete": "CASCADE"}
      },
      "sync_strategy": "full_refresh",
      "notes": "Tabla para identificar a las personas que son super admin"
    },
  #tabla que almacena la informacion de los administradores de la marca personal
  "admin_personal_branding":{
    "primary_key": ["id_admin_personal_branding"],
    "columns": {
      "id_admin_personal_branding": { "type": "INT", "nullable": False },
      "url_photo_profile":          { "type": VARCHARLARGE, "nullable": False,"unique": True },
      "secret_key":                 { "type": VARCHARLARGE,"nullable": False, "unique": True },
      "id_person":                  { "type": "INT", "nullable": False, "fk": KEYPERSON },
      "created_at":                 { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
      "updated_at":                 { "type": "TIMESTAMP", "nullable": True }
    },
    "foreign_keys": {
      "id_person": {"references": KEYPERSON, "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla para identificar a las personas que son administradores de la marca personal"
  },  
  #tabla que almacena el personal branding de las personas
    "personal_branding": {
      "primary_key": ["id_personal_branding"],
      "columns": {
        "id_personal_branding":  { "type": "INT", "nullable": False },
        "name":                  { "type": VARCHARMEDIUM, "nullable": False, "index": True},
        "description":           { "type": "TEXT", "nullable": False},
        "profile_picture_url":   { "type": VARCHARLARGE, "nullable": False},
        "cover_picture_url":     { "type": VARCHARLARGE, "nullable": False},
        "id_person":             { "type": "INT", "nullable": False, "fk": KEYPERSON },
        "created_at":            { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
        "updated_at":            { "type": "TIMESTAMP", "nullable": True }
      },
      "foreign_keys": { 
        "id_person": {"references": KEYPERSON, "on_delete": "CASCADE"}
      },
      "sync_strategy": "full_refresh",
      "notes": "Datos utilizados para personal branding"
    },
  #tabla que almacena las solicitudes de personal branding
    "branding_requests": {
      "primary_key": ["id_super_admin", "id_admin_personal_branding"],
      "columns": {
        "id_super_admin":              { "type": "INT", "nullable": False, "fk": "super_admins.id_super_admin" },
        "id_admin_personal_branding":  { "type": "INT", "nullable": False, "fk": "admin_personal_branding.id_admin_personal_branding" },
        "satus_branding":              { "type": "ENUM( 'pending', 'approved', 'rejected')", "default": "pending", "nullable": False},
        "conten_branding":             { "type": "JSON", "nullable": False},
        "massege_statud":              { "type": VARCHARLARGE, "nullable": False},
        "created_at":                  { "type": "TIMESTAMP", "nullable": False, "default": TODAY },
        "updated_at":                  { "type": "TIMESTAMP", "nullable": True }
      },
      "foreign_keys": {
        "id_super_admin":              { "references": "super_admins.id_super_admin", "on_delete": "CASCADE"},
        "id_admin_personal_branding":  { "references": "admin_personal_branding.id_admin_personal_branding", "on_delete": "CASCADE"}
      },
      "sync_strategy": "full_refresh",
      "notes": "Solicitudes para obtener acceso a las funciones de branding"
    },
  #tabla que almacena los cursos que han sido tomados por los estudiantes
    "admin_courses": {
      "primary_key": "id_admin_courses",
      "columns": {
        "id_admin_courses":    { "type": "INT", "nullable": False },
        "secret_key":          { "type": VARCHARLARGE, "nullable": False },
        "url_photo_profile":   { "type": VARCHARLARGE, "nullable": False },
        "name":                { "type": VARCHARMEDIUM, "nullable": False, "index": True},
        "passed":              { "type": "BOOLEAN", "nullable": False, "default": False },
        "taken_at":            { "type": "TIMESTAMP", "nullable": False, "default": TODAY }
      },
      "sync_strategy": "incremental",
      "sync_key": "taken_at",
      "notes": "Resultados de exámenes"
    },
  #tabla que almacena los curso del sistema 
  "courses":{
    "primary_key": "id_course",
    "columns": {
      "id_course":           { "type": "INT", "nullable": False},
      "name":                { "type": VARCHARMEDIUM, "nullable": False},
      "photo_profile_url":   { "type": VARCHARLARGE, "nullable": False},
      "description":         { "type": "TEXT", "nullable": False},
      "duration_time":       { "type": "INT", "nullable": False},
      "service_policy":      { "type": VARCHARLARGE, "nullable": False},
      "created_at":          { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":          { "type": "TIMESTAMP", "nullable": True}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena los cursos del sistema"
  },
  #tabla que almacena los estudiantes del sistema 
  "students":{
    "primary_key": "id_student",
    "columns": {
      "id_student":          { "type": "INT", "nullable": False},
      "name":                { "type": VARCHARMEDIUM, "nullable": False},
      "photo_profile_url":   { "type": VARCHARLARGE, "nullable": False},
      "id_person":           { "type": "INT", "nullable": True},
      "secret_key":          { "type": VARCHARLARGE, "nullable": False},
      "created_at":          { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":          { "type": "TIMESTAMP", "nullable": True}
    },
    "foreign_keys": {
        "id_person": {"references": KEYPERSON, "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena los estudiantes del sistema"
  },
  #tabla que almaacena la inscripcion de estudiante al curso
  "course_registration":{
    "primary_key": ["id_course_registration"],
    "columns": {
      "id_course_registration": { "type": "INT", "nullable": False},
      "id_student":             { "type": "INT", "nullable": False},
      "id_course":              { "type": "INT", "nullable": False},
      "status":                 { "type": "ENUM('Not started', 'In progress', 'Failed', 'Passed')", "nullable": False, "default": 'Not started'},
      "consent_policy":         { "type": "BOOLEAN", "nullable": False, "default": False},
      "date_registration":      { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":             { "type": "TIMESTAMP", "nullable": True},
      "date_of_compliance":     { "type": "DATE", "nullable": True}
    },
    "foreign_keys": {
        "id_student": {"references": kEYSTUDENT, "on_delete": "CASCADE"},
        "id_course": {"references": KEYCOURSE, "on_delete": "CASCADE"}
    },
    "unique_constraints": {
        "unique_student_course": ["id_student", "id_course"]
    },  
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena la inscripcion de estudiante al curso"
  },
  #tabla que alamacena las resena realizada por el estudiantes
  "student_reviews":{
    "primary_key": "id_review",
    "columns": {
      "id_review":                { "type": "INT", "nullable": False},
      "rating":                   { "type": "INT", "nullable": False},
      "comment":                  { "type": "TEXT", "nullable": True},
      "id_course_registration":   { "type": "INT", "nullable": False, "fk": KEYCOURSEREGITRATION},
      "created_at":               { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":               { "type": "TIMESTAMP", "nullable": True}
    },
    "foreign_keys": {
        "id_course_registration": {"references": KEYCOURSEREGITRATION, "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena las resena realizada por el estudiantes"
  },
  #tabla que almacena la ayuda de cada componente del sistema
  "help_component":{
    "primary_key": "id_help_component",
    "columns": {
      "id_help_component":    { "type": "INT", "nullable": False},
      "name":                 { "type": VARCHARMEDIUM, "nullable": False},
      "description":          { "type": "TEXT", "nullable": False},
      "created_at":           { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":           { "type": "TIMESTAMP", "nullable": True}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena la ayuda de cada componente del sistema"
  },
#tabla que almacena las tareas de los cursos 
  "tasks":{
    "primary_key": "id_task",
    "columns": {
      "id_task":             { "type": "INT", "nullable": False},
      "name":                { "type": VARCHARMEDIUM, "nullable": False},
      "description":         { "type": "TEXT", "nullable": False},
      "created_at":          { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":          { "type": "TIMESTAMP", "nullable": True}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena las tareas de los cursos"
  },
  #tabla que almacena las trampas de telemetria
  "telemetry_tasks":{
    "primary_key":"id_task",
    "columns": {
      "id_task":              { "type": "INT", "nullable": False, "fk": "tasks.id_task"},
      "task_type":            { "type": "ENUM('practical trick', 'question', 'practical activity')", "nullable": False, "default": "question"},
      "payload":              { "type": "JSONB", "nullable": True},
      "created_at":           { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":           { "type": "TIMESTAMP", "nullable": True}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena las tareas de los estudiantes"
  },
  #tabla que alamacena el progreso del estudiante en el curso
  "units": {
    "primary_key": "id_unit",
    "columns": {
      "id_unit":                   { "type": "INT", "nullable": False},
      "name":                      { "type": VARCHARMEDIUM, "nullable": False},
      "description":               { "type": "TEXT", "nullable": False},
      "url_video":                 { "type": VARCHARMEDIUM, "nullable": True},
      "url_written_material":      { "type": VARCHARMEDIUM, "nullable": True},
      "id_course":                 { "type": "INT", "nullable": False, "fk": KEYCOURSE},
      "id_telemetry_task":         { "type": "INT", "nullable": True, "fk": "telemetry_tasks.id_task"},
      "created_at":                { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":                { "type": "TIMESTAMP", "nullable": True}
    },
    "foreign_keys": {
        "id_course": {"references": KEYCOURSE, "on_delete": "CASCADE"},
        "id_telemetry_task": {"references": "telemetry_tasks.id_task", "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena las unidades de los cursos"
  },  
  #tabla que almacena la nota en general 
  "notes":{
    "primary_key": "id_note",
    "columns": {
      "id_note":                     { "type": "INT", "nullable": False},
      "id_course_registration":      { "type": "INT", "nullable": False},
      "id_unit":                     { "type": "INT", "nullable": True},
      "note":                        { "type": "NUMERIC(5,2)", "nullable": False, "default": 0},
      "created_at":                  { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":                  { "type": "TIMESTAMP", "nullable": True}
    },
    "foreign_keys": {
        "id_course_registration": {"references": KEYCOURSEREGITRATION, "on_delete": "CASCADE"},
        "id_unit": {"references": "units.id_unit", "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena la nota en general"
  },
  #tabla que almacena unidad y alumnos 
  "unit_student":{
    "primary_key": ["id_unit", "id_student"],
    "columns": {
      "id_unit":                    { "type": "INT", "nullable": False, "fk": "units.id_unit"},
      "id_student":                 { "type": "INT", "nullable": False, "fk": kEYSTUDENT},
      "unit_completed":             { "type": "BOOLEAN", "nullable": False, "default": False},
      "created_at":                 { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":                 { "type": "TIMESTAMP", "nullable": True}
    },
    "foreign_keys": {
        "id_unit": {"references": "units.id_unit", "on_delete": "CASCADE"},
        "id_student": {"references": kEYSTUDENT, "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena unidad y alumnos"
  },
  #tabla que almacena los maestro
  "teachers":{
    "primary_key": "id_teacher",
    "columns": {
      "id_teacher":     { "type": "INT", "nullable": False},
      "secret_key":     { "type": VARCHARMEDIUM, "nullable": False},
      "photo_url":      { "type": VARCHARMEDIUM, "nullable": True},
      "description":    { "type": "TEXT", "nullable": True},
      "id_person":      { "type": "INT", "nullable": False, "fk": KEYPERSON},
      "created_at":     { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":     { "type": "TIMESTAMP", "nullable": True}
    },
    "foreign_keys": {
        "id_person": {"references": KEYPERSON, "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena los maestros"
  },
  #tabla que almacena los cursos que imparte el maestro
  "teacher_course":{
    "primary_key": ["id_teacher", "id_course"],
    "columns": {
      "id_teacher":            { "type": "INT", "nullable": False, "fk": "teachers.id_teacher"},
      "id_course":             { "type": "INT", "nullable": False, "fk": KEYCOURSE},
      "model_evaluation":      { "type": "ENUM('Unit Notes','Final Note')", "nullable": False},
      "created_at":            { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
      "updated_at":            { "type": "TIMESTAMP", "nullable": True}
    },
    "foreign_keys": {
        "id_teacher": {"references": "teachers.id_teacher", "on_delete": "CASCADE"},
        "id_course": {"references": KEYCOURSE, "on_delete": "CASCADE"}
    },
    "sync_strategy": "full_refresh",
    "notes": "Tabla que almacena los cursos que imparte el maestro"
  },
  #tabla que almacena los reportes de los cursos por estudiante 
   "reports_courses": {
      "primary_key": "id_report",
      "columns": {
        "id_report":           { "type": "INT", "nullable": False },
        "url_pdf":             { "type": VARCHARMEDIUM, "nullable": False},
        "created_at":          { "type": "TIMESTAMP", "nullable": False, "default": TODAY},
        "updated_at":          { "type": "TIMESTAMP", "nullable": True}
      },  
      "sync_strategy": "append_only",
      "notes": "Informes analíticos generados por curso por estudiante"
    }
}
#queda pendiente las futuras vista para realizar analiticas, de momento solo se han creado las tablas relacionales, no se han creado vista 
contract_data:dict= {
    "metadata": metadata,
    "rules": rules,
    "databases": databases,
    "tables": tables
}
