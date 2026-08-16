import pytest
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from backend.infrastructure.contracts.shema_validator import build_column, load_contract, reload_contract
from backend.infrastructure.contracts.exception import ContractsException, struct_contracts, validate_key_secure

# ==========================================
# CONTRATO MOCK PARA PRUEBAS (Una sola tabla)
# ==========================================
mock_contract = {
    "primary_key": "id",
    "columns": {
        "id": {"type": "INT", "nullable": False},
        "username": {"type": "VARCHAR(50)", "nullable": False, "unique": True},
        "is_active": {"type": "BOOLEAN", "default": False, "nullable": False}
    }
}

def get_contract_metadata():
    """Genera el MetaData de SQLAlchemy en memoria basado en el contrato."""
    meta = MetaData()
    columns = []
    for col_name, col_data in mock_contract["columns"].items():
        # Usamos el orquestador del Senior
        col = build_column(col_name, col_data, mock_contract)
        columns.append(col)
    # NOTA DEL SENIOR: Para Alembic compare_metadata, la tabla debe llamarse
    # exactamente igual que en la BD. No usamos "temp_" aquí.
    Table("users", meta, *columns)
    return meta

# ==========================================
# UTILIDAD DE PRUEBA
# ==========================================
def check_migration_against_contract(db_setup_func):
    """
    Crea una DB SQLite en memoria, ejecuta la función db_setup_func que
    simula una migración (creación de tabla), y la compara con el contrato.
    Retorna True si pasó (coinciden) o False y el diff si falló.
    """
    engine = create_engine('sqlite:///:memory:')
    db_meta = MetaData()
    
    # Ejecutamos la "migración" simulada
    db_setup_func(db_meta)
    db_meta.create_all(engine)
    
    # Comparamos
    contract_meta = get_contract_metadata()
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        diff = compare_metadata(context, contract_meta)
    
    if not diff:
        return True, "PASÓ: El contrato se cumplió a la perfección."
    else:
        return False, f"FALLÓ: Contrato roto. Diferencias encontradas:\n{diff}"

# ==========================================
# ESCENARIOS DE PRUEBA (10 MIGRACIONES)
# ==========================================

def _mig_1(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True, nullable=False),
          Column("username", String(50), nullable=False, unique=True),
          Column("is_active", Boolean, default=False, nullable=False))

def _mig_2(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True),
          Column("username", String(50), nullable=False, unique=True))

def _mig_3(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True),
          Column("username", String(50), nullable=False, unique=True),
          Column("email", String(100)), # EXTRA
          Column("is_active", Boolean, nullable=False))

def _mig_4(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True),
          Column("username", Integer, nullable=False), # INCORRECTO
          Column("is_active", Boolean, nullable=False))

def _mig_5(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True),
          Column("username", String(100), nullable=False, unique=True), # LONGITUD MAL
          Column("is_active", Boolean, nullable=False))

def _mig_6(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True),
          Column("username", String(50), nullable=True, unique=True), # NULLABLE TRUE
          Column("is_active", Boolean, nullable=False))

def _mig_7(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True),
          Column("username", String(50), nullable=False, unique=False), # FALTA UNIQUE
          Column("is_active", Boolean, nullable=False))

def _mig_8(meta):
    Table("users", meta,
          Column("id", Integer, nullable=False),
          Column("username", String(50), primary_key=True, nullable=False), # PK MAL
          Column("is_active", Boolean, nullable=False))

def _mig_9(meta):
    Table("user", meta, # NOMBRE MAL
          Column("id", Integer, primary_key=True),
          Column("username", String(50), nullable=False, unique=True),
          Column("is_active", Boolean, nullable=False))

def _mig_10(meta):
    Table("users", meta,
          Column("id", Integer, primary_key=True),
          Column("username", String(50), nullable=False, unique=True),
          Column("is_active", String(10), nullable=False)) # BOOLEAN a STRING

def _run_test_case(mig_func, name, expects_pass=False):
    p, msg = check_migration_against_contract(mig_func)
    if expects_pass:
        print(f"{name}: {msg}")
        return 1 if p else 0
    else:
        status = 'PASÓ' if not p else 'FALLÓ'
        print(f"{name}: {status} (Se esperaba fallo)")
        return 1 if not p else 0

def run_tests():
    print("Iniciando Pruebas de Robustez (10 Escenarios)...\n")
    
    test_cases = [
        (_mig_1, "Test 1 (Migración Perfecta)", True),
        (_mig_2, "Test 2 (Falta Columna is_active)", False),
        (_mig_3, "Test 3 (Columna Extra en DB)", False),
        (_mig_4, "Test 4 (Tipo Dato Incorrecto)", False),
        (_mig_5, "Test 5 (Longitud VARCHAR Diferente)", False),
        (_mig_6, "Test 6 (Nullable Roto)", False),
        (_mig_7, "Test 7 (Falta Constraint UNIQUE)", False),
        (_mig_8, "Test 8 (Primary Key Equivocada)", False),
        (_mig_9, "Test 9 (Tabla Inexistente/Nombre Diferente)", False),
        (_mig_10, "Test 10 (Booleano como String)", False),
    ]

    passed_count = sum(_run_test_case(func, name, expects_pass) for func, name, expects_pass in test_cases)
    total = len(test_cases)

    string_message = "\n--- RESULTADO FINAL DE ROBUSTEZ ---"
    print("-" * len(string_message))
    print(string_message)
    print("-" * len(string_message))
    print(f"{passed_count} de {total} escenarios se comportaron como se esperaba.")
    if passed_count == total:
        print("EL SISTEMA ES SÓLIDO: Alembic detecta exitosamente todas las violaciones al contrato.")
    else:
        print("CUIDADO: Algunos escenarios no reaccionaron adecuadamente.")


def run_exception_tests():
    print("\n\n--- PRUEBAS DE EXCEPCIONES DEL CONTRATO ---\n")
    passed = 0
    total = 6

    # Test 11: Contrato real valido carga correctamente
    try:
        reload_contract()
        c = load_contract()
        assert "metadata" in c
        assert "tables" in c
        print(f"Test 11 (Carga contrato real): PASO - {c['metadata']['contract_name']} v{c['metadata']['version']}")
        passed += 1
    except Exception as e:
        print(f"Test 11 (Carga contrato real): FALLO - {e}")

    # Test 12: Contrato sin "tables" lanza ContractsException
    try:
        bad = {"metadata": {}, "rules": {}, "databases": {}}
        struct_contracts(bad)
        print("Test 12 (Falta tables): FALLO - no lanzo excepcion")
    except ContractsException:
        print("Test 12 (Falta tables): PASO - ContractsException lanzada")
        passed += 1
    except Exception as e:
        print(f"Test 12 (Falta tables): FALLO - excepcion incorrecta: {e}")

    # Test 13: Key con caracter especial lanza ContractsException
    try:
        bad = {"metadata": {}, "rules": {}, "databases": {}, "tables": {"tabla/mala": {}}}
        validate_key_secure(bad)
        print("Test 13 (Key con '/): FALLO - no lanzo excepcion")
    except ContractsException:
        print("Test 13 (Key con '/'): PASO - ContractsException lanzada")
        passed += 1
    except Exception as e:
        print(f"Test 13 (Key con '/'): FALLO - {e}")

    # Test 14: Contrato no es dict lanza ContractsException
    try:
        struct_contracts("no soy un dict")
        print("Test 14 (No es dict): FALLO - no lanzo excepcion")
    except ContractsException:
        print("Test 14 (No es dict): PASO - ContractsException lanzada")
        passed += 1
    except Exception as e:
        print(f"Test 14 (No es dict): FALLO - {e}")

    # Test 15: Seccion es None lanza ContractsException
    try:
        bad = {"metadata": {}, "rules": {}, "databases": {}, "tables": None}
        struct_contracts(bad)
        print("Test 15 (tables es None): FALLO - no lanzo excepcion")
    except ContractsException:
        print("Test 15 (tables es None): PASO - ContractsException lanzada")
        passed += 1
    except Exception as e:
        print(f"Test 15 (tables es None): FALLO - {e}")

    # Test 16: Prototype pollution (__proto__) lanza ContractsException
    try:
        bad = {"metadata": {}, "rules": {}, "databases": {}, "tables": {"__proto__": {}}}
        validate_key_secure(bad)
        print("Test 16 (__proto__): FALLO - no lanzo excepcion")
    except ContractsException:
        print("Test 16 (__proto__): PASO - ContractsException lanzada (inyeccion bloqueada)")
        passed += 1
    except Exception as e:
        print(f"Test 16 (__proto__): FALLO - {e}")

    print("\n--- RESULTADO EXCEPCIONES ---")
    print(f"{passed}/{total} tests de excepcion pasaron.")
    if passed == total:
        print("SISTEMA DE EXCEPCIONES SOLIDO: todas las validaciones de seguridad funcionan.")
    else:
        print(f"CUIDADO: {total - passed} test(s) de excepcion fallaron.")

if __name__ == '__main__':
    run_tests()
    run_exception_tests()
