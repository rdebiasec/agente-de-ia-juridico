from src.gateway.message_content import normalize_message_content, strip_runner_injected_context


def test_normalize_output_text_dict():
    raw = {"annotations": [], "text": "Hola abogado", "type": "output_text", "logprobs": []}
    assert normalize_message_content(raw) == "Hola abogado"


def test_normalize_legacy_python_dict_string():
    raw = "{'annotations': [], 'text': 'Para proceder', 'type': 'output_text', 'logprobs': []}"
    assert normalize_message_content(raw) == "Para proceder"


def test_strip_rag_from_user_message():
    raw = (
        "[Base de conocimiento — fragmentos relevantes]\n"
        "[Fuente 1: proceso-penal-906.md]\n"
        "fragmento\n\n"
        "Verificación browser Postgres"
    )
    assert strip_runner_injected_context(raw) == "Verificación browser Postgres"


def test_strip_rag_legacy_kb_sections():
    raw = (
        "[Base de conocimiento — fragmentos relevantes]\n"
        "[Fuente 1: x.md]\n"
        "foo\n\n"
        "## Etapas\n\n## Rol\n\n"
        "texto largo de la kb\n\n"
        "Verificación browser Postgres"
    )
    assert strip_runner_injected_context(raw) == "Verificación browser Postgres"
