from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List



class RegisterRequest(BaseModel):
    fname: str
    lname: str
    email: str
    pwd: str
    cpwd: str

class LoginRequest(BaseModel):
    email: str
    pwd: str

class UpdateRequest(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    fname: str
    lname: str
    email: str


class ShortenerRequest(BaseModel):
    original_url: str
    ip_address: str 


class ShortenerResponse(BaseModel):
    original_url: str
    shortened_url:str
    qr_code_image: str

class CheckerResponse(BaseModel):
    shortened_url: str
    qr_code_image: str


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
    ip_address: Optional[str] 


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
