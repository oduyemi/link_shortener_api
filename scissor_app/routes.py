import os, random, string, qr_codes, qrcode, base64, bcrypt, hashlib, io, validators, time, urllib.parse
from datetime import datetime
from cachetools import TTLCache, cached
from fastapi import APIRouter, Request, status, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse, RedirectResponse, FileResponse, JSONResponse
from .auth import create_access_token, authenticate_user, verify_token
from sqlalchemy import or_
from sqlalchemy.orm import Session
from scissor_app import app, models, schemas
from passlib.context import CryptContext
from typing import Optional, List
from scissor_app.models import Users, URL, Visit
from .schemas import RegisterRequest, LoginRequest, UserResponse, VisitResponse, ShortenerRequest, QRResponse, VisitDetail
from .dependencies import get_db, get_current_user
from io import BytesIO
from dotenv import load_dotenv
from config import SECRET_KEY, DATABASE_URI
from functools import wraps




load_dotenv()

def hash_password(pwd: str) -> str:
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), salt)
    return hashed_pwd.decode('utf-8')


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)




scissor_router = APIRouter()

cache = TTLCache(maxsize=100, ttl=300)


# URL VALIDATOR
def validate_url(url):
    if url.startswith(('http://', 'https://')) or url.startswith('www.'):
        return True
    return False

# RATE LIMITER
def rate_limiter(max_requests: int, time_frame: int):
    def decorator(func):
        calls = []

        @wraps(func)
        async def wrapper(short_url: str, request: Request, *args, **kwargs):
            now = time.time()
            requests_in_timeframe = [r for r in calls if r > now - time_frame]

            if len(requests_in_timeframe) >= max_requests:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded!")

            calls.append(now)
            return func(short_url, request, *args, **kwargs)

        return wrapper

    return decorator

# GENERATE SHORT URL
def generate_short_url(length=6):
    chars = (string.ascii_letters + string.digits).lower()
    return ''.join(random.choice(chars) for _ in range(length))

# QR CODE IMAGE
def generate_qr_code_image(data: str, qr_codes_path: str = "qr_codes"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)
    url_hash = hashlib.md5(data.encode()).hexdigest()[:10]
    qr_code_path = os.path.join(qr_codes_path, f"{url_hash}.png")
    img.save(qr_code_path)
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    return qr_code_path, img_base64

# QR CODE
def generate_qr_code(data: str, qr_codes_path: str = "qr_codes"):
    qr_image_path = generate_qr_code_image(data, qr_codes_path) 
    with open(qr_image_path, "rb") as f:
        image_bytes = f.read()
    return StreamingResponse(content=image_bytes, media_type="image/png")


@app.get("/")
async def get_index():
    return {"message": "Scissor!"}


@app.post("/register")
async def register_user(user_request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        if user_request.pwd != user_request.cpwd:
            raise HTTPException(status_code=400, detail="Both passwords must match!")

        if not all([user_request.fname, user_request.surname, user_request.email, user_request.pwd, user_request.cpwd]):
            raise HTTPException(status_code=400, detail="All fields are required")

        existing_user = db.query(Users).filter(Users.email == user_request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already taken!")

        hashedpwd = hash_password(user_request.pwd)

        new_user = Users(
            fname=user_request.fname,
            surname=user_request.surname,
            email=user_request.email,
            hashedpwd=hashedpwd,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token = create_access_token({"sub": new_user.email})

        return {
            "fname": new_user.fname,
            "surname": new_user.surname,
            "email": new_user.email,
            "token": token
        }

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise


@app.post("/login")
async def login_user(user_request: LoginRequest, db: Session = Depends(get_db)):
    try:
        if not all([user_request.email, user_request.pwd]):
            raise HTTPException(status_code=400, detail="All fields are required!")

        user = db.query(Users).filter(Users.email == user_request.email).first()
        if not user or not verify_password(user_request.pwd, user.hashedpwd):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        access_token = create_access_token(data={"sub": user.email})

        return JSONResponse(content={
            "access_token": access_token, "token_type": "bearer",
            "user": {
                "id": user.id,
                "fname": user.fname,
                "surname": user.surname,
                "email": user.email
            }
        })
            
    except Exception as e:
        print(f"Error: {e}")
        raise

@app.get("/users", response_model=List[schemas.UserResponse])
async def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(Users).all()

        if not users:
            raise HTTPException(status_code=404, detail="Users not available!")

        user_responses = [
            UserResponse(
                id = user.id,
                fname = user.fname,
                surname = user.surname,
                email = user.email,
            )
            for user in users
        ]

        return user_responses
    except Exception as e:
        print(f"Error: {e}")
        raise


@app.get("/users/{id}", response_model=schemas.UserResponse)
async def get_user(id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(Users).filter(Users.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not available!")

        user_response = schemas.UserResponse(
            id = user.id,
            fname = user.fname,
            surname = user.surname,
            email = user.email,
            hashedpwd = user.hashedPwd
        )

        return user_response
    except Exception as e:
        print(f"Error: {e}")
        raise



@app.post("/shorten-url", response_model=schemas.ShortenerResponse)
def create_short_url(request: ShortenerRequest, db: Session = Depends(get_db)):
    try:
        url = request.original_url
        user_id = request.id
        user = db.query(Users).filter(Users.id == user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        print(f"Received URL: {url}")

        if not validate_url(url):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL")

        hashed = hashlib.md5(url.encode())
        url_hash = base64.urlsafe_b64encode(hashed.digest()).decode('utf-8')[:10]

        db_url = db.query(URL).filter(URL.original_url == url).first()
        if db_url:
            return {
                "original_url": db_url.original_url,
                "shortened_url": db_url.shortened_url,
                "qr_code_image": db_url.qr_code_path,
                "user_id": db_url.user_id
            }

        else:
            short_url = generate_short_url()
            qr_code_path, qr_code_image = generate_qr_code_image(url_hash)

            db_url = URL(
                original_url=url,
                shortened_url=short_url,
                qr_code_path=qr_code_path,
                user_id=user_id
            )
            db.add(db_url)
            db.commit()
            db.refresh(db_url)

            return {
                "original_url": db_url.original_url,
                "shortened_url": db_url.shortened_url,
                "qr_code_image": qr_code_image,
                "user_id": db_url.user_id
            }

    except (HTTPException, Exception) as e:
        print(f"Error: {e}")
        raise



@app.get("/{short_url}", response_model=schemas.ShortenResponse)
@rate_limiter(max_requests=5, time_frame=60)
@cached(cache)
def redirect_to_original(short_url: str, request: Request, db: Session = Depends(get_db)):
    try:
        print(f"Received Shortened URL: {short_url}")
        url = db.query(URL).filter(or_(URL.shortened_url == short_url, URL.original_url == short_url)).first()

        if url is None:
            raise HTTPException(status_code=404, detail="Shortened URL not found")

        url.visit_count += 1

        visit = Visit(
            short_url = short_url,
            url_id = url.id,
            visit_time = datetime.utcnow()
        )
        db.add(visit)
        db.commit()

        link = url.original_url
        if link.startswith("www."):
            link = "https://" + link
        
        print(f"Redirecting to original URL: {link}")

        # Redirect
        return RedirectResponse(link)

    except (HTTPException, Exception) as e:
        print(f"Error: {e}")


@app.get("/get-qr/{short_url}")
@rate_limiter(max_requests=10, time_frame=60)
def get_qr_code(short_url: str, request: Request, db: Session = Depends(get_db)):
    try:
        print(f"Received URL: {short_url}")
        link = db.query(URL).filter(URL.shortened_url == short_url).first()

        if not link:
            raise HTTPException(status_code=404, detail="Link is not valid")

        qr_code_path = link.qr_code_path
        original_url = link.original_url

        response = FileResponse(qr_code_path)
        response.headers["Original-Url"] = original_url

        return response

    except Exception as e:
        print(f"Error: {e}")
        raise


@app.get("/original-url/{short_url}", response_model=schemas.URLResponse)
@cached(cache)
def get_original_url(short_url: str, db: Session = Depends(get_db)):
    try:
        cached_result = cache.get(short_url)
        if cached_result:
            return cached_result

        check = db.query(URL).filter(URL.shortened_url == short_url).first()

        if check:
            response = {
                "shortened_url": check.shortened_url,
                "original_url": check.original_url
            }

            cache[short_url] = response

            return response
        else:
            raise HTTPException(status_code=404, detail="Link is not valid")

    except (HTTPException, Exception) as e:
        print(f"Error: {e}")
        raise 


@app.get("/analytics/{short_url}", response_model=schemas.VisitResponse)
def get_analytics(short_url: str, request: Request, db: Session = Depends(get_db)):
    try:
        print(f"Received URL: {short_url}")
        url = db.query(URL).filter(URL.shortened_url == short_url).first()

        if url is None:
            raise HTTPException(status_code=404, detail="Shortened URL not found")

        visits = db.query(Visit).filter(Visit.short_url == short_url).all()

        response_model = VisitResponse(
            original_url=url.original_url,
            short_url=url.shortened_url,
            visit_times=[VisitDetail(visit_time=visit.visit_time) for visit in visits],
            visit_count=url.visit_count,
            visits=[VisitDetail(visit_time=visit.visit_time) for visit in visits]
        )

        return response_model

    except HTTPException as e:
        print(f"HTTP Exception: {e}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise


@app.get("/link-history/{id}", response_model=list[schemas.LinkHistoryResponse])
def get_link_history(id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(models.Users).filter(models.Users.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        link_history = []
        for url in user.urls:
            visit_count = db.query(models.Visit).filter(models.Visit.url_id == url.id).count()
            visits = db.query(models.Visit).filter(models.Visit.url_id == url.id).all()
            times_visited = [visit.visit_time for visit in visits]

            link_history.append({
                "id": id,
                "original_url": url.original_url,
                "shortened_url": url.shortened_url,
                "visit_count": visit_count,
                "times_visited": times_visited
            })

        return link_history

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
