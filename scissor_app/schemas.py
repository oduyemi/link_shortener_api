from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List



class RegisterRequest(BaseModel):
    fname: str
    surname: str
    email: str
    pwd: str
    cpwd: str

class LoginRequest(BaseModel):
    email: str
    pwd: str


class UserResponse(BaseModel):
    id: int
    fname: str
    surname: str
    email: str


class ShortenerRequest(BaseModel):
    original_url: str
    id: int


class ShortenerResponse(BaseModel):
    original_url: str
    shortened_url:str
    qr_code_image: str
    user_id: int

class LinkHistoryResponse(BaseModel):
    id: int
    original_url: str
    shortened_url: str
    visit_count: int
    times_visited: List[datetime]


class ShortenResponse(BaseModel):
    original_url: str
    shortened_url: str
    qr_code_path: Optional[str]
    visit_count: Optional[int]
    visit_time: Optional[datetime]


class URLRequest(BaseModel):
    id: Optional[int]
    original_url: str
    shortened_url: str
    qr_code_path: Optional[str]
    visit_count: Optional[int]
    visit_time: Optional[datetime]
 


class URLResponse(BaseModel):
    shortened_url: str
    original_url: str


class QRRequest(BaseModel):
    short_url: str


class QRResponse(BaseModel):
    qr_code_path: str
    original_url: str


class VisitDetail(BaseModel):
    visit_time: datetime
    

class VisitResponse(BaseModel):
    original_url: str
    short_url: str
    visit_times: List[VisitDetail]
    visit_count: int
    visits: List[VisitDetail]
