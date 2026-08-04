# Baseline — Validación 7 expertos (2026-08-03 20:43)

## Métricas automáticas

| Métrica | Valor |
|---------|------:|
| generic_io | 0 |
| generic_risk | 0 |
| missing_g10 | 0 |
| missing_g9 | 0 |
| mono_sin_rol | 0 |
| multi_no_boundary | 0 |
| profundizar | 0 |
| total | 81 |
| with_boundary | 75 |
| with_guardrails | 81 |
| with_rol | 80 |
| with_steps | 81 |

## Skills por bloque

### Bloque A (6 skills)

- `estructurar_hechos_fundamentos_solicitudes`
- `redactar_ampliacion_denuncia`
- `redactar_derecho_peticion_penal`
- `redactar_memorial_penal`
- `redactar_recurso_o_intervencion_preliminar`
- `redactar_solicitud_impulso_procesal`

### Bloque B (11 skills)

- `clasificar_aprobacion_juridica`
- `controlar_confidencialidad_datos_sensibles`
- `controlar_no_revictimizacion`
- `controlar_separacion_hecho_inferencia`
- `controlar_tono_juridico_documento`
- `controlar_tono_riesgo_reputacional`
- `detectar_alucinaciones_legales`
- `detectar_riesgo_revictimizacion`
- `revisar_coherencia_estrategica`
- `verificar_citas_normativas`
- `verificar_jurisprudencia`

### Bloque C (13 skills)

- `analizar_intervencion_victima`
- `clasificar_tarea_y_etapa`
- `controlar_terminos_procesales_preliminares`
- `crear_ruta_procesal_recomendada`
- `detectar_riesgos_procesales`
- `detectar_urgencia_penal`
- `evaluar_oportunidad_procesal`
- `evaluar_solicitud_fiscalia_juez`
- `gestionar_faltantes_expediente`
- `identificar_etapa_procesal_ley906`
- `mapear_actuaciones_posibles_victima`
- `marcar_pendientes_verificacion`
- `verificar_hechos_soportados`

### Bloque D (24 skills)

- `analizar_autoria_y_participacion`
- `analizar_dolo_culpa_elemento_subjetivo`
- `clasificar_fuente_factual`
- `clasificar_tipo_prueba`
- `construir_cronologia_penal`
- `construir_matriz_hecho_prueba`
- `controlar_cadena_custodia_preliminar`
- `crear_matriz_hecho_fuente`
- `crear_plan_recaudo_probatorio`
- `descomponer_elementos_tipo_penal`
- `detectar_agravantes_atenuantes`
- `detectar_brechas_probatorias`
- `detectar_contradicciones_factuales`
- `detectar_riesgos_atipicidad`
- `detectar_vacios_factuales`
- `evaluar_suficiencia_probatoria`
- `extraer_hechos_relevantes`
- `generar_preguntas_aclaracion`
- `generar_preguntas_tipicidad`
- `identificar_actores_y_roles`
- `identificar_conductas_punibles_preliminares`
- `inventariar_evidencia`
- `mapear_tipo_penal_hecho_prueba`
- `preservar_evidencia_digital`

### Bloque E (18 skills)

- `alinear_estrategia_prueba_proceso`
- `analizar_derechos_victima`
- `analizar_enfoque_diferencial`
- `construir_teoria_caso_victima`
- `controlar_audiencias`
- `crear_checklist_previo_audiencia`
- `crear_resumen_ejecutivo_litigante`
- `detectar_riesgos_audiencia`
- `evaluar_dano_y_afectacion`
- `generar_preguntas_testigos_peritos`
- `identificar_intereses_victima`
- `identificar_objetivo_audiencia`
- `preparar_contraargumentos`
- `preparar_guion_intervencion_oral`
- `preparar_preguntas_audiencia`
- `preparar_solicitudes_orales`
- `priorizar_objetivos_representacion`
- `simular_escenarios_audiencia`

### Bloque F (9 skills)

- `actualizar_tareas_responsable`
- `crear_reporte_estado_caso`
- `detectar_inactividad_procesal`
- `evaluar_derecho_peticion`
- `generar_alertas_terminos_vencimientos`
- `monitorear_radicado`
- `preparar_resumen_operativo_cliente`
- `registrar_actuacion_procesal`
- `seguimiento_documentos_radicados`

## Lista canónica

```
CHECK FAIL: 1 skills (ej. ['actualizar_tareas_responsable'])
```

## Pytest

```
.....F..F                                                                [100%]
=================================== FAILURES ===================================
__________________ test_audit_progress_history_and_isolation ___________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x10cb2a250>

    @pytest.mark.asyncio
    async def test_audit_progress_history_and_isolation(monkeypatch):
        _audit_env(monkeypatch)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            for email, pin in (("uno@despacho.com", "111111"), ("dos@despacho.com", "222222")):
                r = await client.post(
                    "/api/audit/login",
                    json={
                        "email": email,
                        "password": "audit-test-secret-pass",
                        "new_pin": pin,
                        "accept_privacy": True,
                        "accept_sensitive_data": True,
                    },
                )
                assert r.status_code == 200
    
            r = await client.post(
                "/api/audit/login",
                json={"email": "uno@despacho.com", "password": "audit-test-secret-pass", "pin": "111111"},
            )
            cookies_a = dict(r.cookies)
            r = await client.put("/api/audit/progress", json=_sample_payload(), cookies=cookies_a)
            assert r.status_code == 200
    
            r = await client.post(
                "/api/audit/login",
                json={"email": "dos@despacho.com", "password": "audit-test-secret-pass", "pin": "222222"},
            )
            cookies_b = dict(r.cookies)
            r = await client.get("/api/audit/progress", cookies=cookies_b)
>           assert r.status_code == 404
E           assert 200 == 404
E            +  where 200 = <Response [200 OK]>.status_code

tests/test_compliance.py:117: AssertionError
_______________________ test_audit_logout_clears_session _______________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x10ce6a510>

    @pytest.mark.asyncio
    async def test_audit_logout_clears_session(monkeypatch):
        _audit_env(monkeypatch)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post(
                "/api/audit/login",
                json={
                    "email": "logout@despacho.com",
                    "password": "audit-test-secret-pass",
                    "new_pin": "123456",
                    "accept_privacy": True,
                    "accept_sensitive_data": True,
                },
            )
            assert r.status_code == 200
    
            r = await client.get("/api/audit/session")
            assert r.status_code == 200
            assert r.json()["authenticated"] is True
    
            r = await client.post("/api/audit/logout")
            assert r.status_code == 200
            set_cookie = r.headers.get("set-cookie", "").lower()
            assert "audit_session=" in set_cookie
            assert "max-age=0" in set_cookie
    
            r = await client.get("/api/audit/session")
            assert r.status_code == 200
>           assert r.json()["authenticated"] is False
E           assert True is False

tests/test_compliance.py:177: AssertionError
=============================== warnings summary ===============================
.venv/lib/python3.13/site-packages/alembic/config.py:612
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/alembic/config.py:612: DeprecationWarning: No path_separator found in configuration; falling back to legacy splitting on spaces, commas, and colons for prepend_sys_path.  Consider adding path_separator=os to Alembic config.
    util.warn_deprecated(

tests/test_compliance.py::test_audit_progress_history_and_isolation
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1896: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

tests/test_compliance.py::test_audit_progress_history_and_isolation
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1768: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_compliance.py::test_audit_progress_history_and_isolation - ...
FAILED tests/test_compliance.py::test_audit_logout_clears_session - assert Tr...
2 failed, 7 passed, 3 warnings in 4.30s
```
