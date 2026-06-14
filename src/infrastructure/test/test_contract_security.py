from copy import deepcopy
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
# pyrefly: ignore [missing-import]
from infrastructure.contracts.schema_contracts import contract_data
from infrastructure.contracts.exception import (
    struct_contracts,
    format_exception,
    key_secure,
    validate_key_secure,
    ContractsException,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

PASS = 0
FAIL = 0


def _ok(label: str) -> None:
    global PASS
    PASS += 1
    print(f"   [PASS] {label}")


def _ko(label: str, reason: str = "") -> None:
    global FAIL
    FAIL += 1
    print(f"   [FAIL] {label}" + (f"  -> {reason}" if reason else ""))


def expect_raises(fn, *args, label: str = "") -> bool:
    try:
        fn(*args)
        _ko(label, "se esperaba excepcion pero no ocurrio")
        return False
    except ContractsException:
        _ok(label)
        return True
    except Exception as e:
        _ko(label, f"excepcion incorrecta: {type(e).__name__}")
        return False


def expect_ok(fn, *args, label: str = "") -> bool:
    try:
        fn(*args)
        _ok(label)
        return True
    except ContractsException as e:
        _ko(label, str(e)[:60])
        return False
    except Exception as e:
        _ko(label, f"{type(e).__name__}: {e}")
        return False


# ---------------------------------------------------------------------------
# 1. Contrato real (debe pasar TODO)
# ---------------------------------------------------------------------------

def test_contract_structure() -> None:
    print("\n--- 1. ESTRUCTURA DEL CONTRATO ---")
    expect_ok(struct_contracts, contract_data,
              label="contract_data tiene metadata, rules, databases, tables")

    expect_ok(format_exception, contract_data,
              label="contract_data se serializa sin errores")

    expect_ok(validate_key_secure, contract_data,
              label="claves de contract_data pasan validacion de seguridad")


# ---------------------------------------------------------------------------
# 2. Contrato modificado (casos negativos)
# ---------------------------------------------------------------------------

def test_contract_modified() -> None:
    print("\n--- 2. CONTRATO MODIFICADO (casos negativos) ---")

    # 2a. Sin metadata
    bad = deepcopy(contract_data)
    del bad["metadata"]
    expect_raises(struct_contracts, bad,
                  label="falta metadata -> ContractsException")

    # 2b. Sin rules
    bad = deepcopy(contract_data)
    del bad["rules"]
    expect_raises(struct_contracts, bad,
                  label="falta rules -> ContractsException")

    # 2c. Sin databases
    bad = deepcopy(contract_data)
    del bad["databases"]
    expect_raises(struct_contracts, bad,
                  label="falta databases -> ContractsException")

    # 2d. Sin tables
    bad = deepcopy(contract_data)
    del bad["tables"]
    expect_raises(struct_contracts, bad,
                  label="falta tables -> ContractsException")

    # 2e. Contrato no es dict (es None, lista, string)
    expect_raises(struct_contracts, None,
                  label="contrato es None -> ContractsException")
    expect_raises(struct_contracts, ["lista", "no", "dict"],
                  label="contrato es lista -> ContractsException")
    expect_raises(struct_contracts, "string en vez de dict",
                  label="contrato es string -> ContractsException")


# ---------------------------------------------------------------------------
# 3. Inyeccion / keys maliciosas
# ---------------------------------------------------------------------------

def test_key_injection() -> None:
    print("\n--- 3. INYECCION DE CLAVES ---")

    # 3a. Caracteres prohibidos en key nivel 1
    for bad_key in ["tabla/rota", "columna.exe", "x;DROP", "precio$",
                    "hola:mundo", "a|b", "x`y", "{mal}", "(roto)",
                    "foo<>bar", "hash#tag", "amp&snd", "star*", "q?mark"]:
        fake = {"metadata": {}, "rules": {}, "databases": {}, "tables": {bad_key: {}}}
        expect_raises(validate_key_secure, fake,
                      label=f"key '{bad_key}' -> ContractsException")

    # 3b. Prototype pollution
    for proto in ["__proto__", "constructor", "prototype"]:
        fake = {"metadata": {}, "rules": {}, "databases": {}, "tables": {proto: {}}}
        expect_raises(validate_key_secure, fake,
                      label=f"key reservada '{proto}' -> ContractsException")

    # 3c. Key maliciosa anidada (dentro de tables > students)
    bad = deepcopy(contract_data)
    bad["tables"]["students"]["./shell"] = "payload"
    expect_raises(validate_key_secure, bad,
                  label="key anidada './shell' -> ContractsException")


# ---------------------------------------------------------------------------
# 4. Código vulnerable adicional
# ---------------------------------------------------------------------------

def test_vulnerable_inputs() -> None:
    print("\n--- 4. ENTRADAS VULNERABLES ---")

    # 4a. Dict vacío
    expect_raises(struct_contracts, {},
                  label="dict vacio -> ContractsException")

    # 4b. Metadata existe pero es None
    bad = deepcopy(contract_data)
    bad["metadata"] = None
    expect_raises(struct_contracts, bad,
                  label="metadata es None -> ContractsException")

    # 4c. Tables sin contenido real
    bad = deepcopy(contract_data)
    bad["tables"] = None
    expect_raises(struct_contracts, bad,
                  label="tables es None -> ContractsException")


# ---------------------------------------------------------------------------
# runner automático con contador
# ---------------------------------------------------------------------------

def run_all() -> None:
    global PASS, FAIL
    PASS = 0
    FAIL = 0

    tests = [
        test_contract_structure,
        test_contract_modified,
        test_key_injection,
        test_vulnerable_inputs,
    ]

    for test in tests:
        test()

    total = PASS + FAIL
    print("\n" + "=" * 50)
    print(f"RESULTADO: {PASS}/{total} pasaron, {FAIL}/{total} fallaron")
    if FAIL == 0:
        print("CONTRATO SEGURO - Todas las pruebas superadas")
    else:
        print(f"ATENCION: {FAIL} prueba(s) no superada(s) - revisar salida")


if __name__ == "__main__":
    run_all()
