# Django Typst

A [Django] template engine that uses [Typst] to render Portable Document Format (PDF)
files.

## Installation and Configuration

The Django Typst engine is available from PyPI so you can install it with all the usual
tools:

```shell
pip install django_typst
# or
uv add django_typst
# or
poetry add django_typst
```

Once installed, to make the Typst engine available, you need to add it to the
`TEMPLATES` configuration in your `settings.py`. e.g.:

```python
TEMPLATES = [
    …
    {
        "BACKEND": "django_typst.TypstEngine",
        "NAME": "typst",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "ROOT": None,
            "FONT_PATHS": [],
            "IGNORE_SYSTEM_FONTS": False,
            "PDF_STANDARD": "1.7",
            "PPI": None,
        }
    },
]
```

Note that this should be in _addition_ to the standard Django template engine that was
already there.

All the `OPTIONS` are… optional and the values above represent their defaults should no
alternative be provided.

| Option              | Description                                    | Default  |
| ------------------- | ---------------------------------------------- | -------- |
| ROOT                | The root path to use for relative paths        | `None`\* |
| FONT_PATHS          | Paths to look in for fonts                     | `[]`     |
| IGNORE_SYSTEM_FONTS | Only consider fonts in the defined font paths  | `False`  |
| PDF_STANDARD        | PDF revision to target (`1.7`, `a2-b`, `a3-b`) | `"1.7"`  |
| PPI                 | Pixel Per Inch for included PNG                | `None`   |

\* _The engine with use the folder the template is in as the root if one isn't
specified._

!!! note

    The Django Typst Engine does support loading templates from app dirs with the `APP_DIR`
    configuration, but just like the jinja2 engine, it expects the in-app folder to have an
    engine specific name of `typst`. So if you want to have templates in app directories,
    please ensure they sit within a folder called `typst`.

## Usage

To use this engine with one of the standard Django class based views you only need to
set the `template_engine` class property to the value `"typst"`. You should also set the
`content_type` property to the value `"application/pdf"` to ensure the PDF is returned
with the correct content type. For example, in a simple `TemplateView` it would look
like this:

```python
from django.views import generic

class MyTemplateView(generic.TemplateView):
  template_engine = "typst"
  content_type = "application/pdf"

  …
```

<!-- Links -->

[django]: https://www.djangoproject.com/
[typst]: https://typst.app/
