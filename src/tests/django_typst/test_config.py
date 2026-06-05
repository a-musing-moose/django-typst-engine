import pytest

from django_typst import config


def test_can_create_config_when_options_is_empty():
    tconfig = config.TypstEngineConfig.from_options(options={})

    assert tconfig == config.TypstEngineConfig(
        root=None,
        font_paths=[],
        ignore_system_fonts=False,
        pdf_standard=config.PdfStandard.PDF_1_7,
        ppi=None,
    )


def test_can_set_a_typst_root():
    tconfig = config.TypstEngineConfig.from_options({"ROOT": "/a/path/"})
    assert tconfig.root is not None


def test_can_set_typst_font_paths():
    tconfig = config.TypstEngineConfig.from_options(
        {"FONT_PATHS": ["/a/path/", "/another/path"]}
    )
    assert len(tconfig.font_paths) == 2


def test_can_set_typst_font_paths_with_a_single_value():
    tconfig = config.TypstEngineConfig.from_options({"FONT_PATHS": "/a/path/"})
    assert isinstance(tconfig.font_paths, list)
    assert len(tconfig.font_paths) == 1


def test_can_tell_typst_to_ignore_system_fonts():
    tconfig = config.TypstEngineConfig.from_options({"IGNORE_SYSTEM_FONTS": True})
    assert tconfig.ignore_system_fonts


@pytest.mark.parametrize(
    "standard_name, standard",
    [
        pytest.param("1.7", config.PdfStandard.PDF_1_7, id="PDF Revision 1.7"),
        pytest.param("a-2b", config.PdfStandard.PDF_A_2B, id="PDF Revision a-2b"),
        pytest.param("a-3b", config.PdfStandard.PDF_A_3B, id="PDF Revision a-3b"),
        pytest.param("1.4", config.PdfStandard.PDF_1_4, id="PDF Revision 1.4"),
        pytest.param("1.5", config.PdfStandard.PDF_1_5, id="PDF Revision 1.5"),
        pytest.param("1.6", config.PdfStandard.PDF_1_6, id="PDF Revision 1.6"),
        pytest.param("1.7", config.PdfStandard.PDF_1_7, id="PDF Revision 1.7"),
        pytest.param("2.0", config.PdfStandard.PDF_2_0, id="PDF Revision 2.0"),
        pytest.param("a-1a", config.PdfStandard.PDF_A_1A, id="PDF Revision a-1a"),
        pytest.param("a-1b", config.PdfStandard.PDF_A_1B, id="PDF Revision a-1b"),
        pytest.param("a-2a", config.PdfStandard.PDF_A_2A, id="PDF Revision a-2a"),
        pytest.param("a-2b", config.PdfStandard.PDF_A_2B, id="PDF Revision a-2b"),
        pytest.param("a-2u", config.PdfStandard.PDF_A_2U, id="PDF Revision a-2u"),
        pytest.param("a-3a", config.PdfStandard.PDF_A_3A, id="PDF Revision a-3a"),
        pytest.param("a-3b", config.PdfStandard.PDF_A_3B, id="PDF Revision a-3b"),
        pytest.param("a-3u", config.PdfStandard.PDF_A_3U, id="PDF Revision a-3u"),
        pytest.param("a-4", config.PdfStandard.PDF_A_4, id="PDF Revision a-4"),
        pytest.param("a-4e", config.PdfStandard.PDF_A_4E, id="PDF Revision a-4e"),
        pytest.param("a-4f", config.PdfStandard.PDF_A_4F, id="PDF Revision a-4f"),
        pytest.param("ua-1", config.PdfStandard.PDF_UA_1, id="PDF Revision ua-1"),
    ],
)
def test_can_specify_different_target_pdf_revisions(standard_name, standard):
    tconfig = config.TypstEngineConfig.from_options({"PDF_STANDARD": standard_name})
    assert tconfig.pdf_standard == standard


def test_can_set_target_typst_ppi():
    tconfig = config.TypstEngineConfig.from_options({"PPI": 300})
    assert tconfig.ppi == 300
