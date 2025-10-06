from __future__ import annotations

import dataclasses
import enum
import pathlib
import typing


class PdfStandard(enum.Enum):
    PDF_1_7 = "1.7"
    PDF_A_2B = "a-2b"
    PDF_A_3B = "a-3b"


@dataclasses.dataclass
class TypstEngineConfig:
    root: pathlib.Path | None
    font_paths: list[pathlib.Path]
    ignore_system_fonts: bool
    pdf_standard: PdfStandard
    ppi: int | None

    @classmethod
    def from_options(cls, options: dict[str, typing.Any]) -> TypstEngineConfig:
        root = None
        if root_option := options.pop("ROOT", None):
            root = pathlib.Path(root_option).resolve()

        font_path_option = options.pop("FONT_PATHS", [])
        if not isinstance(font_path_option, list):
            font_path_option = [font_path_option]
        font_paths = [pathlib.Path(p).resolve() for p in font_path_option]

        ignore_system_fonts = False
        if options.pop("IGNORE_SYSTEM_FONTS", None) is True:
            ignore_system_fonts = True

        pdf_standard = PdfStandard.PDF_1_7
        if pdf_standard_option := options.pop("PDF_STANDARD", None):
            pdf_standard = PdfStandard(pdf_standard_option)

        ppi: int | None = None
        if ppi_option := options.pop("PPI", None):
            ppi = int(ppi_option)

        return cls(
            root=root,
            font_paths=font_paths,
            ignore_system_fonts=ignore_system_fonts,
            pdf_standard=pdf_standard,
            ppi=ppi,
        )
