from .config import settings
from .form import Form

from pathlib import Path

import typer
from typing_extensions import Annotated
import uvicorn


app = typer.Typer()


@app.command()
def init(
    output: Annotated[Path, typer.Option(help="Where to write to form file to")]
):
    """Init a new config file."""
    Form.example().to_file(output)


@app.command()
def run(
    config_file: Annotated[Path, typer.Argument(help="Config file")]
):
    """Run the form server."""
    uvicorn.run("forma.server:app", reload=True, port=settings.port) # type: ignore


@app.command()
def merge_translation(
    form_file: Annotated[Path, typer.Option("--form", help="Form file")],
    input_file: Annotated[Path, typer.Option("--input", help="Translated strings")],
    output: Annotated[Path, typer.Option(help="Where to write to file to")],
    target: Annotated[str, typer.Option(help="Code of the target language")]
):
    """Merge the output of an translation into the file."""
    form = Form.from_file(form_file)
    with open(input_file, "r") as file:
        translated = file.read().split("\n")
    form.merge_translation(translated, target)
    form.to_file(output)


@app.command()
def to_translation(
    form_file: Annotated[Path, typer.Option(help="Form file")],
    output: Annotated[Path, typer.Option(help="Where to write to file to")],
    source: Annotated[str, typer.Option(help="State the source language")]
):
    """Export one language version for translation."""
    form = Form.from_file(form_file)
    with open(output, "w") as file:
        file.write(form.to_translation(source))


if __name__ == "__main__":
    app()