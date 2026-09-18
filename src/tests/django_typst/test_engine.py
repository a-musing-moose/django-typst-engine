from unittest import mock

import pytest
import tomlkit
from django.template import Origin, TemplateDoesNotExist

from django_typst import config, encoding, engine


class StubContextEncoder(encoding.ContextEncoder):
    def encode(self, context):
        return "encoded context"

# Engine Tests


def test_engine_compliance():
    tengine = engine.TypstEngine(params={"DIRS": [], "APP_DIRS": True})
    assert hasattr(tengine, "from_string")
    assert hasattr(tengine, "get_template")
    assert hasattr(tengine, "app_dirname")


def test_engine_can_create_template_from_a_string():
    tengine = engine.TypstEngine(params={"DIRS": [], "APP_DIRS": True})

    template = tengine.from_string("= A Title")

    assert isinstance(template, engine.TypstTemplate)
    assert template.origin.name == engine.UNKNOWN_SOURCE
    assert template.origin.loader is None
    assert template.config == tengine.config


def test_engine_raises_correct_exception_if_template_file_not_found(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    tengine = engine.TypstEngine(params={"DIRS": [str(template_dir)], "APP_DIRS": True})
    with pytest.raises(TemplateDoesNotExist) as exc_info:
        tengine.get_template("unobtainium.typ")

    assert len(exc_info.value.tried) == 2  # template dir _and_ app typst dir
    dir_tried = exc_info.value.tried[0]
    assert dir_tried[0].name == str(template_dir / "unobtainium.typ")


def test_engine_can_find_template(tmp_path):
    template_dirs = [tmp_path / "templates", tmp_path / "others"]
    for t in template_dirs:
        t.mkdir()

    template_file = template_dirs[1] / "some.typ"
    template_file.write_text("= Howdy")

    tengine = engine.TypstEngine(
        params={
            "DIRS": [str(template_dirs[0]), str(template_dirs[1])],
            "APP_DIRS": False,
        }
    )

    found = tengine.get_template("some.typ")
    assert isinstance(found, engine.TypstTemplate)
    assert found.origin.name == str(template_file)
    assert found.config == tengine.config


def test_engine_can_find_template_in_app_dir():
    tengine = engine.TypstEngine(
        params={
            "DIRS": [],
            "APP_DIRS": True,
        }
    )

    found = tengine.get_template("app_dir_template.typ")
    assert isinstance(found, engine.TypstTemplate)
    assert found.origin.name.endswith("example_app/typst/app_dir_template.typ")
    assert found.config == tengine.config


# Template Tests


def test_can_render_string_template():
    template_code = b"= Whoop, Whoop!"
    engine_config = config.TypstEngineConfig.from_options({})

    template = engine.TypstTemplate(template_code=template_code, config=engine_config)

    assert template.origin.name == engine.UNKNOWN_SOURCE

    pdf = template.render()
    assert isinstance(pdf, bytes)


def test_uses_template_path_as_root_dir(tmp_path, monkeypatch):
    template_path = tmp_path / "templates"

    origin = Origin(name=str(template_path / "some.typ"), template_name="some.typ")

    template_code = b"= Whoop, Whoop!"
    engine_config = config.TypstEngineConfig.from_options({})

    template = engine.TypstTemplate(
        template_code=template_code, config=engine_config, origin=origin
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
        template_code=template_code,
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


def test_template_uses_the_configured_context_encoder(monkeypatch):
    template_code = b"= Whoop, Whoop!"
    engine_config = config.TypstEngineConfig.from_options(
        {"CONTEXT_ENCODER": f"{__name__}.StubContextEncoder"}
    )
    template = engine.TypstTemplate(template_code=template_code, config=engine_config)
    mock_compile = mock.Mock(return_value=b"")
    monkeypatch.setattr(engine.typst, "compile", mock_compile)

    template.render({"name": "J Moss"})

    assert mock_compile.call_args.kwargs["sys_inputs"] == {"context": "encoded context"}
