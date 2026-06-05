from __future__ import annotations

import dataclasses
import enum
import pathlib
import typing


class PdfStandard(enum.Enum):
    PDF_1_4 = "1.4"
    PDF_1_5 = "1.5"
    PDF_1_6 = "1.6"
    PDF_1_7 = "1.7"
    PDF_2_0 = "2.0"
    PDF_A_1A = "a-1a"
    PDF_A_1B = "a-1b"
    PDF_A_2A = "a-2a"
    PDF_A_2B = "a-2b"
    PDF_A_2U = "a-2u"
    PDF_A_3A = "a-3a"
    PDF_A_3B = "a-3b"
    PDF_A_3U = "a-3u"
    PDF_A_4 = "a-4"
    PDF_A_4E = "a-4e"
    PDF_A_4F = "a-4f"
    PDF_UA_1 = "ua-1"    


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
        if root_option := options.get("ROOT", None):
            root = pathlib.Path(root_option).resolve()

        font_path_option = options.get("FONT_PATHS", [])
        if not isinstance(font_path_option, list):
            font_path_option = [font_path_option]
        font_paths = [pathlib.Path(p).resolve() for p in font_path_option]

        ignore_system_fonts = False
        if options.get("IGNORE_SYSTEM_FONTS") is True:
            ignore_system_fonts = True

        pdf_standard = PdfStandard.PDF_1_7
        if pdf_standard_option := options.get("PDF_STANDARD", None):
            pdf_standard = PdfStandard(pdf_standard_option)

        ppi: int | None = None
        if ppi_option := options.get("PPI", None):
            ppi = int(ppi_option)

        return cls(
            root=root,
            font_paths=font_paths,
            ignore_system_fonts=ignore_system_fonts,
            pdf_standard=pdf_standard,
            ppi=ppi,
        )
