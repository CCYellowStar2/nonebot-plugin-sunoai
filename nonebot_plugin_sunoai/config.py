from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    suno_key: str = ""  # （必填）第三方sunoai API KEY


class ConfigError(Exception):
    pass