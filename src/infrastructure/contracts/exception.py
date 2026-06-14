import json
import re
class ContractsException(Exception):
    def __init__(self, message, data):
        super().__init__(message)
        self.data = data
    
def format_exception(json_contracts: dict):
    try:
        json.dumps(json_contracts, default=str)
        return json_contracts
    except (json.JSONDecodeError, TypeError) as e:
        raise ContractsException("Error al serializar el JSON del contrato", str(e))

REQUIRED_SECTIONS = ["metadata", "rules", "databases", "tables"]


def struct_contracts(json_contract: dict, path: str = "") -> dict:
    if not isinstance(json_contract, dict):
        raise ContractsException("El contrato en la posicion " + path + " debe ser un diccionario", json_contract)
    for section in REQUIRED_SECTIONS:
        if section not in json_contract:
            raise ContractsException("El contrato en la posicion " + path + " debe tener " + section, json_contract)
        if not isinstance(json_contract[section], dict):
            raise ContractsException("La seccion " + section + " en " + path + " debe ser un diccionario", json_contract[section])
    validate_key_secure(json_contract)
    return json_contract
def key_secure(key:str):
    if re.search(r"[./\\:;|$`{}()<>#&*?]", key):
        raise ContractsException("La llave no es segura. Violación de seguridad. Intento de inyección. Caracteres especiales detectados", key)
    if key in ["__proto__", "constructor", "prototype"]:
        raise ContractsException("La llave no es segura. Violación de seguridad. Intento de inyección. Palabras reservadas", key)    
    return key

def validate_key_secure(json_contracts: dict,path:str="" ):
    for key, value in json_contracts.items():
        key_secure(key)
        if isinstance(value, dict):
            validate_key_secure(value, f"{path}.{key}")
        