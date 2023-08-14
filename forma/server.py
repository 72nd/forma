from .form import AvailableForms, Form

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="template")


class FormNotFoundException(Exception):
    def __init__(self, requested_ident: str):
        self.requested_ident = requested_ident


@app.exception_handler(FormNotFoundException)
async def form_not_found_exception_handler(
    request: Request,
    exception: FormNotFoundException,
):
    data = {
        "request": request,
        "requested_ident": exception.requested_ident,
    }
    return templates.TemplateResponse("form_not_found_error.html.jinja2", data, status_code=404)


@app.get("/")
async def root(
    request: Request,
):
    data = {"request": request}
    return templates.TemplateResponse("index.html.jinja2", data)


@app.get("/form/{ident}")
async def form(
    request: Request,
    ident: str,
    forms: dict[str, Form] = AvailableForms,
):
    if ident not in forms:
        raise FormNotFoundException(ident)
    data = {
        "request": request,
        "ident": ident,
    }
    return templates.TemplateResponse("form.html.jinja2", data)


@app.get("/api/form/{ident}")
async def api_form(
    ident: str,
    forms: dict[str, Form] = AvailableForms,
):
    if ident not in forms:
        raise HTTPException(
            status_code=404,
            detail=f"no form found for given ident '{ident}",
        )
    form = forms[ident]
    form.password = None
    return form