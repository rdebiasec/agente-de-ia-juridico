# Checklist RNBD / SIC — bases de datos personales

**No es un registro automático.** El despacho (responsable) decide con abogado de cumplimiento si debe registrar bases ante la SIC según Ley 1581 y normas reglamentarias vigentes.

## Inventario de bases del producto

| Base / tabla | Titulares | Categoría | Sensibles | Canal |
|--------------|-----------|-----------|-----------|-------|
| `chat_sessions` | Usuarios despacho / datos de casos ingresados | Profesional + caso | Posible | Web |
| `drafts` | Contenido jurídico de víctimas/terceros | Caso | Alta | Web/Slack |
| `session_traces` | Previews de consultas | Caso | Posible | Web |
| `expedientes` | Partes, radicado, flags menor/sensible | Caso | Alta si flags | Web |
| `compliance_consent` | Consentimientos + IP/UA | Identificación | No | Web/Portal |
| `audit_portal_*` | Correo abogada, progreso, PIN hash | Profesional | No | Portal |
| `execution_plans` | Mensaje del abogado + plan | Profesional | Baja–media | Web/Slack |
| `document_chunks` | Texto de expediente/KB | Caso / KB | Posible | Web |

## Preguntas de decisión (llenar con abogado)

1. ¿El responsable es DBX Solutions u otro despacho cliente?  
2. ¿Hay bases de datos de carácter personal sujetas a inscripción según el régimen vigente?  
3. ¿Los datos de víctimas se tratan solo bajo mandato profesional (relación abogado-cliente) con autorización expresa?  
4. ¿Se documentó el encargado OpenAI/Render/Slack?  
5. ¿Hay menores de edad como titulares en expediente (`involucra_menor=true`)? → medidas reforzadas.

## Salida esperada

- [ ] Acta interna de decisión (registrar / no registrar / actualizar)  
- [ ] Si aplica: número de radicado RNBD o constancia SIC  
- [ ] Fecha de próxima revisión: ________  

Contacto ARCO producto: `privacidad@dbxsolutions.com`
