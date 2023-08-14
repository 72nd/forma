import typed_settings

@typed_settings.settings
class Settings:
    port: int
    """Port the web-server should run on."""
    forms: list[str]
    """List of path pointing to form definition files."""


settings = typed_settings.load(Settings, appname="forma", config_files=["settings.toml", ".secrets.toml"])
