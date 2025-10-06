import typing

from django.conf import settings
from django.template import Template, TemplateDoesNotExist
from django.template.backends.base import BaseEngine
from django.template.backends.django import reraise

from . import config, engine


class TypstEngine(BaseEngine):  # type: ignore[misc]
    """
    A template engine for rendering Typst templates.
    """

    app_dirname = "typst"

    def __init__(self, params: dict[str, typing.Any]) -> None:
        params = params.copy()
        params.setdefault("NAME", "typst")
        options = params.pop("OPTIONS", {})
        options.setdefault("debug", settings.DEBUG)
        options.setdefault("file_charset", "utf-8")
        loaders = ["django.template.loaders.filesystem.Loader"]
        if params["APP_DIRS"]:
            loaders += ["django.template.loaders.app_directories.Loader"]
            loaders = [("django.template.loaders.cached.Loader", loaders)]
        self.config = config.TypstEngineConfig.from_options(options)
        super().__init__(params)
        self.engine = engine.TypstEngine(
            self.config, dirs=self.dirs, app_dirs=self.app_dirs, **options
        )

    def from_string(self, template_code):
        return self.engine.from_string(template_code)

    def get_template(self, template_name: str) -> Template:
        try:
            return self.engine.get_template(template_name)
        except TemplateDoesNotExist as exc:
            return reraise(exc, self)
