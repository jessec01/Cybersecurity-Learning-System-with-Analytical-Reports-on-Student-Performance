import sys
import os
# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from sqlalchemy import MetaData, Column
# pyrefly: ignore [missing-import]
from sqlalchemy import Column

# Aseguramos que el directorio src esté al principio del path para los imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def test_shema_validator_import():
    """Prueba que el módulo shema_validator se pueda importar sin errores."""
    try:
        from infrastructure.contracts import shema_validator
    except Exception as e:
        pytest.fail(f"EXPLOTÓ al importar shema_validator: {e}")

def _validate_column(table_name, col_name, col_data, table_info):
    """Función auxiliar para validar una sola columna (reduce complejidad cognitiva)."""
    from infrastructure.contracts.shema_validator import (
        parse_type, parse_constraints, parse_foreign_key, build_column
    )
    
    phrase = f"Parseo de columna {col_name} de {table_name} fallido"
    
    # 1. Test parse_type
    col_type = parse_type(col_data)
    assert col_type is not None, f"{phrase} -> parse_type() retornó None"
    
    # 2. Test parse_constraints
    constraints = parse_constraints(col_data)
    assert isinstance(constraints, dict), f"{phrase} -> parse_constraints() no retornó dict"
    
    # 3. Test parse_foreign_key
    fk = parse_foreign_key(col_data)
    fk_raw = col_data.get("fk")
    if fk_raw:
        assert fk is not None, f"parse_foreign_key() retornó None para fk: {fk_raw}"
    
    # 4. Test build_column
    col_obj = build_column(col_name, col_data, table_info)
    assert isinstance(col_obj, Column), f"{phrase} -> build_column() no retornó Column"
    
    # Verificar primary key
    pk_info = table_info.get("primary_key", [])
    if isinstance(pk_info, str):
        pk_info = [pk_info]
    
    expected_pk = col_name in pk_info
    assert expected_pk == col_obj.primary_key, f"PK incorrecta: esperado={expected_pk}, actual={col_obj.primary_key}"
    
    # Verificar nullable
    if "nullable" in col_data:
        assert col_data["nullable"] == col_obj.nullable, f"{phrase} -> Nullable incorrecto"

def test_table_columns_parsing()->None:
    """Itera sobre el contrato y prueba el parseo de cada columna individualmente."""
    from infrastructure.contracts.schema_contracts import contract_data
    from infrastructure.contracts.shema_validator import (
        parse_type, parse_constraints, parse_foreign_key, build_column
    )
    tables = contract_data.get("tables", {})
    problemas = []
    for table_name, table_info in tables.items():
        columns = table_info.get("columns", {})
        for col_name, col_data in columns.items():
            try:
                _validate_column(table_name, col_name, col_data, table_info)
            except Exception as e:
                problemas.append(f"{table_name}.{col_name} -> {type(e).__name__}: {str(e)}")
                
    if problemas:
        pytest.fail("Fallos encontrados en validación de columnas:\n" + "\n".join(problemas))

def test_build_table_completo():
    """Prueba que todas las tablas del contrato se puedan construir en memoria dinámicamente."""
    from infrastructure.contracts.schema_contracts import contract_data
    from infrastructure.contracts.shema_validator import build_table
    
    metadata_temporal = MetaData()
    problemas = []
    
    for table_name, table_data in contract_data.get("tables", {}).items():
        try:
            table_obj = build_table(table_name, table_data, metadata_temporal)
            
            # Verificar nombre temporal
            assert table_obj.name == f"temp_{table_name}", f"Nombre incorrecto {table_obj.name}"
            
            # Verificar número de columnas
            expected_columns = len(table_data.get("columns", {}))
            actual_columns = len(table_obj.columns)
            assert expected_columns == actual_columns, f"Columnas: esperado={expected_columns}, actual={actual_columns}"
            
        except Exception as e:
            problemas.append(f"{table_name} -> {type(e).__name__}: {str(e)}")
            
    if problemas:
        pytest.fail("Fallos en build_table:\n" + "\n".join(problemas))

def test_validate_contract_db_import():
    """Asegura que el flujo principal de validación de contrato esté presente."""
    try:
        from infrastructure.contracts.shema_validator import validate_contract_db
    except Exception as e:
        pytest.fail(f"Error al importar validate_contract_db: {e}")

if __name__ == '__main__':
    # Permite ejecutar con "python test_conversor.py" y que invoque a pytest automáticamente
    pytest.main(["-v", __file__])