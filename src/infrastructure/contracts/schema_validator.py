# pyrefly: ignore [missing-import]
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    text,
    create_engine,
    Boolean, Date, Numeric, Text, JSON, Float, DECIMAL
)
import re
# pyrefly: ignore [missing-import]
from infrastructure.contracts.schema_contracts import contract_data
# pyrefly: ignore [missing-import]
from infrastructure.contracts.exception import (
    ContractsException, format_exception, struct_contracts
)


# ==========================================
# DELEGACIÓN FASE 2: Parseo de Tipos de Datos (ESP Ticket 2.1)
# ==========================================
def _parse_enum_values(type_str: str) -> tuple:
    raw = re.findall(r"'([^']*)'", type_str)
    return tuple(raw) if raw else ()


def parse_type(col_data: dict):
    raw_type = str(col_data.get("type", "VARCHAR(255)")).strip()

    if re.match(r"ENUM\s*\(.+\)", raw_type, re.IGNORECASE):
        values = _parse_enum_values(raw_type)
        sorted_key = "_".join(v.replace(" ", "_") for v in sorted(values))[:50]
        name = f"enum_{sorted_key}"
        return Enum(*values, name=name)

    match = re.match(r"VARCHAR\s*\(\s*(\d+)\s*\)", raw_type, re.IGNORECASE)
    if match:
        return String(int(match.group(1)))

    match = re.match(r"NUMERIC\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", raw_type, re.IGNORECASE)
    if match:
        return Numeric(int(match.group(1)), int(match.group(2)))

    type_map = {
        "INT":        Integer,
        "INTEGER":    Integer,
        "BOOLEAN":    Boolean,
        "BOOL":       Boolean,
        "TIMESTAMP":  DateTime,
        "DATE":       Date,
        "TEXT":       Text,
        "JSON":       JSON,
        "JSONB":      JSON,
        "FLOAT":      Float,
        "DECIMAL":    DECIMAL,
        "UUID":       String(36),
    }

    for key, sa_type in type_map.items():
        if raw_type.upper() == key:
            return sa_type() if callable(sa_type) else sa_type

    raise ContractsException(
        f"Tipo de dato no soportado: {raw_type}",
        col_data
    )


# ==========================================
# DELEGACIÓN FASE 3: Mapeo de Constraints (JR1 / ESP)
# ==========================================
def parse_constraints(col_data: dict) -> dict:
    kwargs = {}

    if "nullable" in col_data:
        kwargs["nullable"] = col_data["nullable"]
    if "unique" in col_data:
        kwargs["unique"] = col_data["unique"]
    if "index" in col_data:
        kwargs["index"] = col_data["index"]

    raw_default = col_data.get("default")
    if raw_default is not None:
        _inject_default(kwargs, raw_default, col_data.get("type", ""))

    return kwargs


def _inject_default(kwargs: dict, raw_default, col_type_hint: str) -> None:
    if isinstance(raw_default, bool):
        kwargs["default"] = raw_default
        return

    if isinstance(raw_default, (int, float)):
        kwargs["default"] = raw_default
        return

    raw_str = str(raw_default).strip()
    type_upper = str(col_type_hint).upper()

    if raw_str.upper() in ("NOW()", "CURRENT_TIMESTAMP"):
        kwargs["server_default"] = text("NOW()")
        return

    if re.match(r"ENUM\s*\(.+\)", type_upper, re.IGNORECASE):
        kwargs["default"] = raw_str.lstrip("'").rstrip("'")
        return

    if raw_str.upper() == "NULL":
        kwargs["server_default"] = text("NULL")
        return

    if type_upper in ("BOOLEAN", "BOOL") or raw_str.upper() in ("TRUE", "FALSE"):
        kwargs["default"] = raw_str.upper() == "TRUE"
        return

    kwargs["default"] = raw_str.lstrip("'").rstrip("'")


# ==========================================
# DELEGACIÓN FASE 4: Llaves Foráneas (ESP Ticket 4.2)
# ==========================================
def parse_foreign_key(col_data: dict):
    fk_raw = col_data.get("fk")
    if not fk_raw:
        return None
    return ForeignKey(fk_raw)


# ==========================================
# FASE 1 y 4: Arquitectura Base y Primary Keys (SNR)
# ==========================================
def build_column(col_name: str, col_data: dict, table_metadata: dict) -> Column:
    col_type = parse_type(col_data)
    kwargs = parse_constraints(col_data)

    pk_info = table_metadata.get("primary_key", [])
    if isinstance(pk_info, str):
        pk_info = [pk_info]

    if col_name in pk_info:
        kwargs["primary_key"] = True

    fk = parse_foreign_key(col_data)

    if fk is not None:
        return Column(col_name, col_type, fk, **kwargs)
    else:
        return Column(col_name, col_type, **kwargs)


def build_table(table_name: str, table_metadata: dict, metadata_obj: MetaData,
                use_temp: bool = True) -> Table:
    columns_objs = []
    columns_dict = table_metadata.get("columns", {})

    for col_name, col_data in columns_dict.items():
        col_obj = build_column(col_name, col_data, table_metadata)
        columns_objs.append(col_obj)

    tbl_name = f"temp_{table_name}" if use_temp else table_name
    extras = {"prefixes": ["TEMPORARY"]} if use_temp else {}
    return Table(tbl_name, metadata_obj, *columns_objs, **extras)


# ==========================================
# CARGA SEGURA DEL CONTRATO (validacion de formato + keys)
# ==========================================
_contract_cache = None


def load_contract():
    global _contract_cache
    if _contract_cache is not None:
        return _contract_cache
    try:
        validated = struct_contracts(format_exception(contract_data))
    except ContractsException as e:
        raise ContractsException(
            f"CONTRATO CORRUPTO - {e}. El sistema no puede iniciar.",
            e.data
        )
    _contract_cache = validated
    return validated


def reload_contract():
    global _contract_cache
    _contract_cache = None
    return load_contract()


# ==========================================
# FASE 5: Validación de Operaciones contra Contrato (ESP)
# ==========================================
def contract_enforce_operations(rules: dict):
    blocked = []
    if rules.get("allow_delete_tables", False) is False:
        blocked.append("DELETE (tabla)")
    if rules.get("allow_drop_table", False) is False:
        blocked.append("DROP TABLE")
    if rules.get("allow_rename_tables", False) is False:
        blocked.append("RENAME TABLE")
    if rules.get("allow_delete_columns", False) is False:
        blocked.append("DELETE (columna)")
    if rules.get("allow_rename_columns", False) is False:
        blocked.append("RENAME COLUMN")
    if rules.get("allow_new_tables", False) is False:
        blocked.append("CREATE TABLE (nueva)")
    return blocked


def classify_diff(diff_list: list, rules: dict) -> dict:
    blocked_ops = contract_enforce_operations(rules)
    result = {"allowed": [], "blocked": [], "blocked_reason": blocked_ops}

    if not diff_list:
        return result

    for item in diff_list:
        item_str = str(item)
        blocked = False
        for op in blocked_ops:
            if op.lower().replace(" ", "_") in item_str.lower().replace(" ", "_"):
                blocked = True
                break
        if blocked:
            result["blocked"].append(item_str)
        else:
            result["allowed"].append(item_str)

    return result


# ==========================================
# FLUJO PRINCIPAL: Transaccion de Migracion
# ==========================================
def run_migration_check(db_url: str) -> dict:
    contract = load_contract()
    rules = contract.get("rules", {})

    metadata_contract = MetaData()
    metadata_real = MetaData()

    for table_name, table_metadata in contract.get("tables", {}).items():
        build_table(table_name, table_metadata, metadata_contract, use_temp=False)

    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            with conn.begin() as trans:
                metadata_contract.create_all(conn, checkfirst=False)
                metadata_real.reflect(bind=conn)

                # comparison contract vs real
                # comparamos metadata_contract (sin temp) contra metadata_real
                # pyrefly: ignore [missing-import]
                from alembic.migration import MigrationContext
                # pyrefly: ignore [missing-import]
                from alembic.autogenerate import compare_metadata
                ctx = MigrationContext.configure(conn)
                diff = compare_metadata(ctx, metadata_contract)

                if diff:
                    classification = classify_diff(diff, rules)
                    if classification["blocked"]:
                        trans.rollback()
                        return {
                            "status": "BLOCKED",
                            "reason": f"Operaciones bloqueadas: {classification['blocked_reason']}",
                            "blocked_ops": classification["blocked"],
                            "allowed_ops": classification["allowed"],
                        }
                    trans.commit()
                    return {
                        "status": "WARNING",
                        "reason": "Cambios detectados pero permitidos por el contrato",
                        "allowed_ops": classification["allowed"],
                    }

                trans.rollback()
                return {
                    "status": "OK",
                    "reason": "Migraciones validas. El contrato se cumple.",
                }

    finally:
        engine.dispose()


# ==========================================
# VALIDACION CON CONTRATO EN MEMORIA (sin DB real)
# ==========================================
def validate_contract_db():
    try:
        contract = load_contract()
        rules = contract.get("rules", {})

        metadata_temporal = MetaData()

        print("--- INICIANDO CONVERSION DINAMICA ---")
        tables_dict = contract.get("tables", {})
        for table_name, table_metadata in tables_dict.items():
            build_table(table_name, table_metadata, metadata_temporal, use_temp=True)
            print(f"Tabla '{table_name}' orquestada en memoria.")

        print("--- CONVERSION EXITOSA ---")

        blocked = contract_enforce_operations(rules)
        print("\n--- RESTRICCIONES DEL CONTRATO ---")
        print(f"  allow_new_tables:     {rules.get('allow_new_tables')}")
        print(f"  allow_delete_tables:  {rules.get('allow_delete_tables')}")
        print(f"  allow_new_columns:    {rules.get('allow_new_columns')}")
        print(f"  allow_delete_columns: {rules.get('allow_delete_columns')}")
        print(f"  allow_rename_columns: {rules.get('allow_rename_columns')}")
        print(f"  allow_rename_tables:  {rules.get('allow_rename_tables')}")
        print(f"\n  OPERACIONES BLOQUEADAS: {blocked}")
        print("  PERMITIDO: INSERT, UPDATE, SELECT, ALTER TABLE ADD COLUMN")

        # -- PLAN PARA VALIDACION DE OWNERS (FUTURO) --
        # Cuando se active la DB real, antes de ejecutar la migracion:
        # 1. Leer databases.backend.owner y databases.data_engineering.owner
        # 2. Comparar con current_user de PostgreSQL (SELECT current_user)
        # 3. Si current_user coincide con owner del backend → permisos totales
        # 4. Si current_user es data_engineering → solo SELECT
        # 5. Si current_user no esta en el contrato → DENEGAR todo
        # Implementar con: conn.execute(text("SELECT current_user")).scalar()

    except ContractsException as e:
        print(f"CONTRATO CORRUPTO: {e}")
        print(f"Datos del error: {e.data}")
    except Exception as e:
        print(f"Error critico en el flujo de validacion: {e}")


if __name__ == '__main__':
    validate_contract_db()
