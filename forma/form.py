from .config import settings

from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from fastapi import Depends
from pydantic import BaseModel
from pydantic import Field as PdField
from pydantic_yaml import parse_yaml_file_as, to_yaml_file

LocStr = Union[str, dict[str, str]]

def get_ls(item: LocStr, key: str) -> str:
    if isinstance(item, dict):
        return item[key]
    return item

def set_ls(item: LocStr, key: str, value: str) -> LocStr:
    if isinstance(item, dict):
        item[key] = value
        return item
    return value

class Type(str, Enum):
    """Has Many or Many To Many columns."""
    LINK_TO_ANOTHER_RECORD = "link_to_another_record"
    """For short text."""
    SINGLE_LINE_TEXT = "single_line_text"
    """For lengthy string content."""
    LONG_TEXT = "long_text"
    """File attachment column."""
    ATTACHMENT = "attachment"
    """Boolean value."""
    CHECKBOX = "checkbox"
    """Multiple options can be selected once."""
    MULTI_SELECT = "multi_select"
    """Single option select."""
    SINGLE_SELECT = "single_select"
    """Date selector."""
    DATE = "date"
    """Year selector."""
    YEAR = "year"
    """Time selector."""
    TIME = "time"
    """Phone number field."""
    PHONE_NUMBER = "phone_number"
    """Email field."""
    EMAIL = "email"
    """Valid URL field."""
    URL = "url"
    """Any type of number."""
    NUMBER = "number"
    """Fractional number."""
    DECIMAL = "decimal"
    """Currency value."""
    CURRENCY = "currency"
    """Percentage."""
    PERCENT = "percent"
    """Duration."""
    DURATION = "duration"
    """Rating."""
    RATING = "rating"
    """Formula based generated column."""
    FORMULA = "formula"
    """Performs calculations and aggregations."""
    ROLLUP = "rollup"
    """Date & Time selector."""
    DATE_TIME = "date_time"
    """QR Code visualization of another referenced column."""
    Q_CODE = "q_code"
    """Barcode visualization of another referenced column."""
    BARCODE = "barcode"
    """Geometry column."""
    GEOMETRY = "geometry"
    """GeoData column."""
    GEO_DATA = "geo_data"
    """Json column."""
    JSON = "json"
    """Custom DB type option."""
    SPECIFIC_DB_TYPE = "specific_db_type"
    """Defines a section header in the form."""
    PARAGRAPH = "paragraph"
    """Defines a paragraph of text in the form. Content is title as heading and description"""


class Field(BaseModel):
    name: str
    field_type: Type = PdField(alias="type")
    title: LocStr
    default: Optional[Any] = None
    placeholder: Optional[LocStr] = None
    icon: Optional[str] = None
    required: bool = False
    description: Optional[LocStr]
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    step: Optional[float] = None

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def single_line_text_example(cls) -> "Field":
        return cls(
            name = "first_name",
            type = Type.SINGLE_LINE_TEXT,
            title = {
                "de": "Vorname",
                "en": "First Name",
            },
            icon = "fa-regular fa-user",
            placeholder = "Anna Mueller",
            required = True,
            description = {
                "de": "Gib bitte dein Vorname an",
                "en": "Please enter your first name",
            },
            min_length = 2,
            max_length = 200,
            min_value = None,
            max_value = None,
        )

    @classmethod
    def number_example(cls) -> "Field":
        return cls(
            name = "age",
            type = Type.NUMBER,
            title = {
                "de": "Alter",
                "en": "Age",
            },
            default = 23,
            description = {
                "de": "Gib bitte dein Alter an",
                "en": "Please enter your Age",
            },
            min_length = None,
            max_length = None,
            min_value = 18,
            max_value = 200,
        )

    def merge_translation(self, items: list[str], target: str):
        set_ls(self.title, target, items[0])
        if self.description:
            set_ls(self.description, target, items[1])

    def to_translation(self, source: str) -> list[str]:
        rsl: list[str] = []
        rsl.append(get_ls(self.title, source))
        if self.description:
            rsl.append(get_ls(self.description, source))
        else:
            rsl.append("")
        return rsl

class Form(BaseModel):
    ident: str
    password: Optional[str] = None
    title: LocStr
    text_top: Optional[LocStr]
    text_bottom: Optional[LocStr]
    languages: dict[str, str]
    default_language: str
    fields: list[Field]

    @classmethod
    def example(cls) -> "Form":
        return cls(
            title = {
                "de": "Bewerbung",
                "en": "Application",
            },
            ident = "application",
            text_top = {
                "de": "Bitte geben sie folgende Daten an.",
                "en": "Please fill out this form.",
            },
            text_bottom = {
                "de": "Vielen Dank für Ihre Zeit.",
                "en": "Thank you for filling out this form.",
            },
            languages = {
                "de": "Deutsch",
                "en": "English",
            },
            default_language = "de",
            fields = [
                Field.single_line_text_example(),
                Field.number_example(),
            ],
        )

    @classmethod
    def from_file(cls, path: Path) -> "Form":
        return parse_yaml_file_as(Form, path)

    def to_file(self, path: Path):
        to_yaml_file(path, self, exclude_none=True, by_alias=True)
    
    def merge_translation(self, items: list[str], target: str):
        if target not in self.languages:
            self.languages[target] = f"TODO ({target})"
            print(f"language {target} added to supported languages, please add name")
        set_ls(self.title, target, items[0])
        if self.text_top:
            set_ls(self.text_top, target, items[1])
        if self.text_bottom:
            set_ls(self.text_bottom, target, items[2])
        i = 3
        for field in self.fields:
            field.merge_translation(items[i:i+2], target)
            i += 2

    def to_translation(self, source: str) -> str:
        rsl: list[str] = []
        if source not in self.languages:
            raise KeyError(f"given source language {source} is not a form language")
        rsl.append(get_ls(self.title, source))
        if self.text_top:
            rsl.append(get_ls(self.text_top, source))
        else:
            rsl.append("")
        if self.text_bottom:
            rsl.append(get_ls(self.text_bottom, source))
        else:
            rsl.append("")
        for field in self.fields:
            rsl.extend(field.to_translation(source))
        return "\n".join(rsl)
        

forms_cache: dict[str, Form] = {}


def get_forms() -> dict[str, Form]:
    if len(forms_cache) == 0:
        for path in settings.forms:
            form = Form.from_file(Path(path))
            forms_cache[form.ident] = form
    return forms_cache


AvailableForms = Depends(get_forms)