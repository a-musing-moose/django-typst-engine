from django_typst import engine


def test_engine_compliance():
    tengine = engine.TypstEngine(params={"DIRS": [], "APP_DIRS": True})
    assert hasattr(tengine, "from_string")
    assert hasattr(tengine, "get_template")
