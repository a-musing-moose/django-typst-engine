from __future__ import annotations

import pathlib
import typing

import tomlkit
import typst
from django.http.request import HttpRequest
from django.template import Origin
from django.template.engine import Engine

from . import config

UNKNOWN_SOURCE = "<unknown source>"


class TypstEngine(Engine):
    def __init__(self, config: config.TypstEngineConfig, **kwargs):
        self.config = config
        super().__init__(**kwargs)

    def from_string(self, template_code: str) -> TypstTemplate:
        return TypstTemplate(
            source=template_code.encode(self.file_charset), config=self.config
        )

    def get_template(self, template_name):
        """
        Return a compiled Template object for the given template name,
        handling template inheritance recursively.
        """
        template, origin = self.find_template(template_name)
        if not hasattr(template, "render"):
            # template needs to be compiled
            return TypstTemplate(
                source=template.encode(self.file_charset),
                config=self.config,
                origin=origin,
            )
        return TypstTemplate(
            source=template.source.encode(self.file_charset),
            config=self.config,
            origin=origin,
        )


class TypstTemplate:
    """
    A Typst template that can be rendered.
    """

    def __init__(
        self,
        source: bytes,
        config: config.TypstEngineConfig,
        origin: Origin | None = None,
    ):
        self.source = source
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
