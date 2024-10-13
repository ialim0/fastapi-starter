from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, ClassVar

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    oauth_provider: Optional[str] = None

    config: ClassVar[ConfigDict] = {"from_attributes": True}
