# Antes y ahora — Guardrails Input / Output / Tools

Resumen simple.

---

## Tabla rápida

| Qué | Antes | Ahora |
|---|---|---|
| Agentes con trío input / output / tools | 1 | 10 |
| Especialistas con freno de entrada | 0 | 9 |
| Materias de otros equipos Lexiatek | Se mencionaban y “reconducían” mucho | Fuera de alcance breve; este asistente no las desarrolla |
| Pruebas de cobertura I/O/T | Casi ninguna | Suite en verde |

---

## Qué significa

- **Entrada:** ¿dejo pasar este pedido?
- **Salida:** ¿la respuesta es usable y segura?
- **Tools:** ¿puedo llamar esta herramienta con estos datos?

Este asistente es **solo penal-víctimas**. Otras líneas Lexiatek las atiende otro equipo: aquí no se ofrecen ni se detallan.

---

## Dónde mirar

- Políticas: `config/guardrails/agents/{agente}/`
- Código: `src/agents/sdk_guardrails.py`
- Pruebas: `tests/test_guardrails_iot_coverage.py`
