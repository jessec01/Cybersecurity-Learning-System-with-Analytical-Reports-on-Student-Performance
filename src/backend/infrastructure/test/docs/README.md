# Documentacion de Tests

## Indice de archivos

| Archivo | Tipo | Tests | Requiere DB | Docs |
|---------|------|-------|-------------|------|
| `test_domain.py` | Unitario | 14 | No | [docs/test_domain.md](test_domain.md) |
| `test_jwt.py` | Unitario | 3 | No | [docs/test_jwt.md](test_jwt.md) |
| `test_permissions.py` | Unitario | 7 | No | [docs/test_permissions.md](test_permissions.md) |
| `test_repositories.py` | Integracion | 12 | SQLite en memoria | [docs/test_repositories.md](test_repositories.md) |
| `test_super_admin_flow.py` | Integracion | 25 | SQLite en memoria | [docs/test_super_admin_flow.md](test_super_admin_flow.md) |
| `test_contract_full_flow.py` | Integracion | 14 | SQLite en memoria | [docs/test_contract_full_flow.md](test_contract_full_flow.md) |
| `test_api.py` | API / E2E | 13 | PostgreSQL real | [docs/test_api.md](test_api.md) |
| `test_manual_cases.py` | Manual | 5 flujos | DB + Redis real | [docs/test_manual_cases.md](test_manual_cases.md) |
| **Total** | | **83** | | |

## Orden de ejecucion

```
1. Unitarios (sin DB ni Redis)
   test_domain.py         → logica pura de entidades
   test_jwt.py            → encode/decode de tokens
   test_permissions.py    → constantes y formato resource:action

2. Integracion (SQLite en memoria)
   test_repositories.py         → CRUD de repositorios
   test_super_admin_flow.py     → flujo CLI completo
   test_contract_full_flow.py   → contrato + ORM + use cases

3. API / E2E (requiere PostgreSQL + Redis corriendo)
   test_api.py            → endpoints HTTP
   test_manual_cases.py   → flujos manuales documentados
```

## Comando rapido

```bash
# Unitarios (rapido, 0 dependencias)
pytest test_domain.py test_jwt.py test_permissions.py -v

# Integracion (SQLite en memoria)
pytest test_repositories.py test_super_admin_flow.py test_contract_full_flow.py -v

# Todo (menos API que requiere PostgreSQL)
pytest test_domain.py test_jwt.py test_permissions.py test_repositories.py test_super_admin_flow.py test_contract_full_flow.py -v
```
