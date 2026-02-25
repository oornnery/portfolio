from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SEOMeta(BaseModel):
    title: str
    description: str = Field(max_length=160)
    og_image: str = ""
    og_type: str = "website"
    canonical_url: str = ""
    keywords: list[str] = Field(default_factory=list)


class ContactForm(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    csrf_token: str

    model_config = ConfigDict(extra="forbid")


class ContactResponse(BaseModel):
    success: bool
    message: str
    errors: dict[str, str] = Field(default_factory=dict)
