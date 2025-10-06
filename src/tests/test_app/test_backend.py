import pytest
from django.template import TemplateDoesNotExist

from django_typst import backend, engine

# Backend Tests


def test_backend_compliance():
    tengine = backend.TypstEngine(params={"DIRS": [], "APP_DIRS": True})
    assert hasattr(tengine, "from_string")
    assert hasattr(tengine, "get_template")
    assert hasattr(tengine, "app_dirname")


def test_backend_can_create_template_from_a_string():
    tengine = backend.TypstEngine(params={"DIRS": [], "APP_DIRS": True})

    template = tengine.from_string("= A Title")

    assert isinstance(template, engine.TypstTemplate)
    assert template.origin.name == engine.UNKNOWN_SOURCE
    assert template.origin.loader is None
    assert template.config == tengine.config


def test_backend_raises_correct_exception_if_template_file_not_found(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    tengine = backend.TypstEngine(
        params={"DIRS": [str(template_dir)], "APP_DIRS": True}
    )
    with pytest.raises(TemplateDoesNotExist) as exc_info:
        tengine.get_template("unobtainium.typ")

    assert len(exc_info.value.tried) == 2
    dir_tried = exc_info.value.tried[0]
    assert dir_tried[0].name == str(template_dir / "unobtainium.typ")


def test_backend_can_find_template(tmp_path):
    template_dirs = [tmp_path / "templates", tmp_path / "others"]
    for t in template_dirs:
        t.mkdir()

    template_file = template_dirs[1] / "some.typ"
    template_file.write_text("= Howdy")

    tengine = backend.TypstEngine(
        params={
            "DIRS": [str(template_dirs[0]), str(template_dirs[1])],
            "APP_DIRS": True,
        }
    )

    found = tengine.get_template("some.typ")
    assert isinstance(found, engine.TypstTemplate)
    assert found.origin.name == str(template_file)
    assert found.config == tengine.config


def test_backend_can_find_app_dir_template():
    tengine = backend.TypstEngine(
        params={
            "DIRS": [],
            "APP_DIRS": True,
        }
    )

    found = tengine.get_template("app_dir_template.typ")
    assert isinstance(found, engine.TypstTemplate)
    assert found.origin.loader_name == "django.template.loaders.app_directories.Loader"
    assert found.origin.template_name == "app_dir_template.typ"
    assert found.config == tengine.config
