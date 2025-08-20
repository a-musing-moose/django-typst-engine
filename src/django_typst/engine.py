from __future__ import annotations

import pathlib
import typing

import tomlkit
import typst
from django.http.request import HttpRequest
from django.template import Origin, TemplateDoesNotExist
from django.template.backends.base import BaseEngine

from . import config

UNKNOWN_SOURCE = "<unknown source>"


class TypstEngine(BaseEngine):  # type: ignore[misc]
    """
    A template engine for rendering Typst templates.
    """

    def __init__(self, params: dict[str, typing.Any]) -> None:
        params = params.copy()
        params.setdefault("NAME", "typst")
        options = params.pop("OPTIONS", {})
        self.config = config.TypstEngineConfig.from_options(options)
        super().__init__(params)

    def from_string(self, template_code: str) -> TypstTemplate:
        return TypstTemplate(
            template_code=template_code.encode("utf-8"), config=self.config
        )

    def get_template(self, template_name: str) -> TypstTemplate:
        tried = []

        for template_path in self.iter_template_filenames(template_name):
            path = pathlib.Path(template_path)
            origin = Origin(
                name=path.as_posix(),
                template_name=template_name,
            )
            tried.append((origin, template_name))

            if path.exists() and path.is_file():
                template_code = path.read_bytes()
                return TypstTemplate(
                    template_code=template_code, config=self.config, origin=origin
                )

        raise TemplateDoesNotExist(template_name, tried=tried, backend=self)


class TypstTemplate:
    """
    A Typst template that can be rendered.
    """

    def __init__(
        self,
        template_code: bytes,
        config: config.TypstEngineConfig,
        origin: Origin | None = None,
    ):
        self.source = template_code
        self.config = config
        if origin is None:
            self.origin = Origin(UNKNOWN_SOURCE)
        else:
            self.origin = origin

    def render(
        self,
        context: dict[str, typing.Any] | None = None,
        request: HttpRequest | None = None,
    ) -> bytes:
        if context is None:
            context = {}

        context.pop("view", None)  # views are not toml serializable

        if request:
            context["request"] = request

        root = self.config.root
        if not root and self.origin.name != UNKNOWN_SOURCE:
            # Use the directory containing the template as the root unless set in
            # options.
            root = pathlib.Path(self.origin.name).parent

        return typing.cast(
            bytes,
            typst.compile(  # type: ignore[call-overload]
                input=self.source,
                root=root.as_posix() if root else None,
                font_paths=[p.as_posix() for p in self.config.font_paths],
                ignore_system_fonts=self.config.ignore_system_fonts,
                ppi=self.config.ppi,
                sys_inputs={"context": tomlkit.dumps(context)},
                pdf_standards=self.config.pdf_standard.value,
            ),
        )
