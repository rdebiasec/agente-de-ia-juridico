# Fase 1 — MVP (consulta, redacción y comunicación)

**Épica Jira:** KAN-6  
**Tareas:** KAN-11, KAN-12, KAN-13  
**Prerequisito:** Completar Fase 0

## Objetivo

Primera versión funcional: atender consultas, analizar riesgos, redactar contratos y escritos básicos, comunicarse con clientes.

## Estado de la fase

- **Activa**
- Restricción de canales: operación web/API interna. No activar Slack/WhatsApp en Fase 1.
- Regla inmutable: la IA propone; el abogado revisa y aprueba.
- Seguridad jurídica: no inventar sentencias, radicados ni normas.

## Requisitos Fase 1

### KAN-11 — Atención y comunicación con clientes

- **REQ-012 (Prioritario):** Brindar atención permanente a los clientes.
- **REQ-013 (Prioritario):** Manejar situaciones delicadas con los clientes.
- **REQ-014 (Prioritario):** Explicar en lenguaje sencillo los escenarios jurídicos.
- **REQ-015 (Importante):** Redactar correos corporativos y mensajes profesionales.

### KAN-12 — Análisis de consultas, riesgos y estrategia

- **REQ-016 (Prioritario):** Identificar riesgos jurídicos durante la consulta.
- **REQ-017 (Prioritario):** Convertir hechos en narrativas ordenadas y convincentes.
- **REQ-018 (Prioritario):** Diferenciar cuándo un asunto es civil o penal.
- **REQ-019 (Prioritario):** Construir teorías del caso.
- **REQ-020 (Específico):** Identificar pruebas faltantes.
- **REQ-021 (Importante):** Detectar debilidades en escritos y contestaciones.

### KAN-13 — Redacción básica: contratos y escritos

- **REQ-024 (Prioritario):** Redactar contratos complejos y personalizados.
- **REQ-025 (Prioritario):** Blindar contratos para proteger intereses del cliente.
- **REQ-026 (Específico):** Redactar contratos de prestación de servicios, inversión y alianzas.
- **REQ-027 (Importante):** Preparar escritos para jueces, fiscales, comisarías y entidades.
- **REQ-028 (Específico):** Elaborar recursos, solicitudes y excepciones.

## Capacidades habilitadas

- Atención y comunicación con clientes
- Análisis de consultas, riesgos y estrategia
- Redacción básica: contratos y escritos

## Fuera de alcance en Fase 1

- Fase 2: REQ-022, REQ-023 y REQ-043..050 (seguimiento de procesos y rol estratégico ampliado).
- Fase 3: REQ-029..042 (conceptos, memoriales y tutelas).
- Integraciones operativas por canales externos (Slack/WhatsApp) para atención productiva.

## Criterios de aceptación

1. Fase activa en runtime configurada en `1`.
2. Solicitudes de KAN-11, KAN-12 y KAN-13 responden dentro de alcance.
3. Solicitudes de Fase 2 y Fase 3 se bloquean con mensaje claro de capacidad no activa.
4. Toda respuesta mantiene disclaimer de revisión humana sin duplicados.
5. Pruebas automatizadas y validación de rúbrica para Fase 1 en verde.
