from pydantic import BaseModel, EmailStr, Field, constr, ConfigDict
from typing import Optional, ClassVar

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)

    config: ClassVar[ConfigDict] = {
        "str_min_length": 1,
        "str_strip_whitespace": True,
    }
