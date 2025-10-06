from unittest import mock

import tomlkit
from django.template import Origin

from django_typst import config, engine

# Template Tests


def test_can_render_string_template():
    template_code = b"= Whoop, Whoop!"
    engine_config = config.TypstEngineConfig.from_options({})

    template = engine.TypstTemplate(source=template_code, config=engine_config)

    assert template.origin.name == engine.UNKNOWN_SOURCE

    pdf = template.render()
    assert isinstance(pdf, bytes)


def test_uses_template_path_as_root_dir(tmp_path, monkeypatch):
    template_path = tmp_path / "templates"

    origin = Origin(name=str(template_path / "some.typ"), template_name="some.typ")

    template_code = b"= Whoop, Whoop!"
    engine_config = config.TypstEngineConfig.from_options({})

    template = engine.TypstTemplate(
        source=template_code, config=engine_config, origin=origin
    )

    mock_compile = mock.Mock(return_value=b"")
    monkeypatch.setattr(engine.typst, "compile", mock_compile)

    template.render()

    mock_compile.assert_called_once_with(
        input=template_code,
        root=str(template_path),
        font_paths=[],
        ignore_system_fonts=False,
        ppi=None,
        sys_inputs={"context": ""},
        pdf_standards="1.7",
    )


def test_request_is_passed_to_typst_if_supplied(monkeypatch, rf):
    template_code = b"= Whoop, Whoop!"
    request = rf.get("/some/path/or/other")

    engine_config = config.TypstEngineConfig.from_options({})

    template = engine.TypstTemplate(
        source=template_code,
        config=engine_config,
    )

    mock_compile = mock.Mock(return_value=b"")
    monkeypatch.setattr(engine.typst, "compile", mock_compile)

    template.render(request=request)

    mock_compile.assert_called_once_with(
        input=template_code,
        root=None,
        font_paths=[],
        ignore_system_fonts=False,
        ppi=None,
        sys_inputs=mock.ANY,
        pdf_standards="1.7",
    )

    sys_input = mock_compile.call_args[1]["sys_inputs"]
    context = tomlkit.loads(sys_input["context"])
    assert "request" in context
    assert isinstance(context["request"], dict)
