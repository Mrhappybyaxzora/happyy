from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, Query, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from happy.database import MongoDB, User, History, Message, Session
from happy.assistant import Assistant, queryModifier
from happy.mail import resetpassword
from hashlib import sha256
from datetime import datetime, timezone
from typing import Optional, List
from happy.assistant.llm.gemini import upload_to_gemini, wait_for_files_active

from rich import print
from dataclasses import asdict
import json
import asyncio
import io
import re
import base64
import os
import aiofiles
import uuid

# App Init -----------------------------------------------------------------
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
# App Init -----------------------------------------------------------------/

# Database Init ------------------------------------------------------------
db = MongoDB()

file_db: dict[str, File] = {}
# Database Init ------------------------------------------------------------/

# Hash Function ------------------------------------------------------------
hashof = lambda fullname, email, password: sha256(
    f"{fullname}{email}{password}".encode("utf-8")
).hexdigest()
# Hash Function ------------------------------------------------------------/


@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
    return await http_exception_handler(request, exc)


# index route
@app.route("/", methods=["GET", "POST"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# login html
@app.get("/login")
async def login_page(request: Request):
    if "user" in request.session:
        return RedirectResponse("/happy", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    if user := db.getUser(Email=email):
        if user.Password == password:
            import json
            from datetime import datetime

            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return super().default(obj)

            request.session["user"] = json.dumps(user.to_dict(), cls=DateTimeEncoder)
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "messages": [{"type": "success", "content": "Login successful"}],
                },
            )
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "messages": [
                {"type": "error", "content": "Email or password is incorrect"}
            ],
        },
    )


@app.get("/register")
async def register_page(request: Request):
    if "user" in request.session:
        return RedirectResponse("/happy", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: bool = Form(...),
):
    print(f"{name = }, {email = }, {password = }, {confirm_password = }, {terms = }")
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "messages": [{"type": "error", "content": "Passwords do not match"}],
            },
        )
    if not terms:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "messages": [
                    {
                        "type": "error",
                        "content": "You must agree to the terms and conditions",
                    }
                ],
            },
        )
    if len(password) < 1:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "messages": [
                    {
                        "type": "warning",
                        "content": "Password should be at least 8 characters long",
                    }
                ],
            },
        )

    if db.getUser(Email=email) is not None:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "messages": [
                    {"type": "error", "content": "Email already exists, please login"}
                ],
            },
        )

    db.insertUser(
        User(
            _id=hashof(name, email, password),
            FullName=name,
            Age=None,
            Email=email,
            Address=None,
            Gender=None,
            DOB=None,
            Height=None,
            InputLanguage=None,
            AssistantVoice=None,
            ContactNumber=None,
            Password=password,
            CreatedAt=datetime.now(timezone.utc),
        )
    )

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "messages": [
                {"type": "success", "content": "Account created successfully"}
            ],
        },
    )


@app.get("/forgot-password")
def forgot_password_page(request: Request):
    if "user" in request.session:
        return RedirectResponse("/happy", status_code=302)
    return templates.TemplateResponse("forget-password.html", {"request": request})


@app.post("/forget-password")
async def forget_password(request: Request, email: str = Form(...)):
    user = db.getUser(Email=email)
    if user:
        resetpassword(user)
        return templates.TemplateResponse(
            "forget-password.html",
            {
                "request": request,
                "messages": [
                    {
                        "type": "success",
                        "content": "Password reset link sent to your email",
                    }
                ],
            },
        )
    return templates.TemplateResponse(
        "forget-password.html",
        {
            "request": request,
            "messages": [{"type": "error", "content": "Email not found"}],
        },
    )


@app.get("/logout")
def logout(request: Request):
    return templates.TemplateResponse("logout.html", {"request": request})


def is_mobile(user_agent: Optional[str]) -> bool:
    mobile_regex = re.compile(
        r".*(iphone|android|blackberry|webos|windows phone|opera mini|mobile).*",
        re.IGNORECASE,
    )
    return bool(mobile_regex.match(user_agent))



@app.get("/happy")
def happy(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=302)

    user_agent = request.headers.get("user-agent", "").lower()
    if is_mobile(user_agent):
        return templates.TemplateResponse(
            "happy-mobile.html",
            {
                "request": request,
                "user": request.session["user"],
                "FullName": json.loads(request.session["user"])["FullName"],
                "history": get_history(json.loads(request.session["user"])["_id"]),
            },
        )
    else:
        return templates.TemplateResponse(
            "happy-pc.html",
            {
                "request": request,
                "user": request.session["user"],
                "FullName": json.loads(request.session["user"])["FullName"],
                "history": get_history(json.loads(request.session["user"])["_id"]),
            },
        )


@app.post("/happy")
async def happy_post(request: Request):
    # Get form data
    form_data = await request.form()
    print("Received POST data:", dict(form_data))
    user = json.loads(request.session["user"])
    for key, value in dict(form_data).items():
        if value != "":
            user[key] = value
    print(user)
    request.session["user"] = json.dumps(user)
    db.updateUser(User(**user))
    # Return the same template response as GET
    user_agent = request.headers.get("user-agent", "").lower()
    if is_mobile(user_agent):
        return templates.TemplateResponse(
            "happy-mobile.html",
            {
                "request": request,
                "user": request.session["user"],
                "FullName": json.loads(request.session["user"])["FullName"],
                "history": get_history(json.loads(request.session["user"])["_id"]),
            },
        )
    else:
        return templates.TemplateResponse(
            "happy-pc.html",
            {
                "request": request,
                "user": request.session["user"],
                "FullName": json.loads(request.session["user"])["FullName"],
                "history": get_history(json.loads(request.session["user"])["_id"]),
            },
        )


@app.get("/notepad", response_class=HTMLResponse)
async def read_item(request: Request, content: str = "Start typing..."):
    return templates.TemplateResponse(
        "notepad.html", {"request": request, "content": content}
    )

@app.get("/image-pad")
async def image_pad(request: Request, url: str = "url"):
    return templates.TemplateResponse("image-pad.html", {"request": request, "url": url})

@app.get("/download")
async def download_file(
    content: str = Query(..., description="Content to be included in the file")
):
    # Create an in-memory file-like object
    file_like = io.BytesIO(content.encode("utf-8"))
    file_like.seek(0)

    # Create a StreamingResponse
    response = StreamingResponse(
        file_like,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=text.txt"},
    )
    return response


def get_history(_id):
    history = db.getHistory(_id=_id)
    if history is None:
        history = History(
            _id=_id,
            CreatedAt=datetime.now(timezone.utc),
            LastModified=datetime.now(timezone.utc),
            Sessions=[],
        )
        db.insertHistory(history)
    past_messages = db.sessionsToMessages(history.Sessions[-3:], rmtimestamp=True)
    return past_messages


@app.websocket("/c/ws")
async def websocket_endpoint(ws: WebSocket):
    user = ws.session.get("user", None)
    if user is None:
        await ws.close()
    await asyncio.sleep(2)
    user: dict = json.loads(user)
    try:
        userDetailsToSend = {"user": {}}
        
        whatToSend = ["FullName", "Email", "Address", "Age", "Gender", "DOB", "Height", "InputLanguage", "ContactNumber"]
        for key in whatToSend:
            if user[key]:
                userDetailsToSend["user"][key] = user[key]

        await ws.accept()
        await ws.send_text(json.dumps(userDetailsToSend))
    
        stt = datetime.now(timezone.utc)
        ai = Assistant(user, [])

        history = db.getHistory(_id=user["_id"])
        if history is None:
            history = History(
                _id=user["_id"],
                CreatedAt=datetime.now(timezone.utc),
                LastModified=datetime.now(timezone.utc),
                Sessions=[],
            )
            db.insertHistory(history)
        past_messages = db.sessionsToMessages(history.Sessions[-3:], rmtimestamp=True)
        current_messages = []

        openaiformat = lambda li: [{"role": x.role, "content": x.content} for x in li]

        while True:
            message = await ws.receive_text()
            if message == "ping":
                await ws.send_text("pong")
            elif message == "undefined":
                pass
            else:
                data_received = json.loads(message)
                # prompt = queryModifier(data_received["prompt"])
                prompt: str = data_received["prompt"]
                imgbase64Url = data_received.get("imgbase64", None)
                files = data_received.get("files", None)
                print(f"{files = }")
                real_files = []
                if files is not None:
                    for file in files:
                        real_files.append(file_db[file["url"]])
                doNotSaveUserQ = False
                
                if prompt.lower() == "[user is inactive]":
                    doNotSaveUserQ = True
                    print("User is inactive")
                    print(f"{prompt = }")
                response = await ai.run(
                    prompt, imgbase64Url, real_files, past_messages + openaiformat(current_messages)
                )
                if response.text:
                    if not doNotSaveUserQ:
                        current_messages.append(Message("user", prompt[11:] if "TTCAMTOKENTT".lower() in prompt.lower() else prompt, datetime.now()))
                    current_messages.append(
                        Message("assistant", response.text, datetime.now())
                    )
                if response.images:
                    new_urls = []
                    for image in response.images:
                        file_name = sha256(image.encode("utf-8")).hexdigest()
                        with open(f"static/images/{file_name}.png", "wb") as f:
                            f.write(base64.b64decode(image.replace("data:image/png;base64,", "")))
                        new_urls.append(f"/static/images/{file_name}.png")
                    response.images = new_urls
                await ws.send_text(json.dumps(asdict(response)))

    except WebSocketDisconnect:
        current_session = Session(
            StartedAt=stt, EndedAt=datetime.now(timezone.utc), Messages=current_messages
        )
        db.insertSession(user["_id"], current_session)

    except Exception as e:
        current_session = Session(
            StartedAt=stt, EndedAt=datetime.now(timezone.utc), Messages=current_messages
        )
        db.insertSession(user["_id"], current_session)
        print(e)


UPLOAD_DIR = "static/uploads"
ALLOWED_EXTENSIONS = {
    # Documents
    '.txt', '.pdf', '.doc', '.docx', '.rtf', '.odt',
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    # Audio
    '.mp3', '.wav', '.ogg', '.m4a', '.flac',
    # Video
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
    # Archives
    '.zip', '.rar', '.7z',
}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB in bytes

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def is_allowed_file(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS

def secure_filename(filename: str) -> str:
    # Get the file extension
    ext = os.path.splitext(filename)[1]
    # Create a new filename with UUID
    return f"{uuid.uuid4()}{ext}"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Check if file type is allowed
        if not is_allowed_file(file.filename):
            return {"error": "File type not allowed"}, 400

        # Check file size
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        # Create a temporary file to check size
        temp_file_path = os.path.join(UPLOAD_DIR, "temp")
        async with aiofiles.open(temp_file_path, 'wb') as temp_file:
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    os.remove(temp_file_path)
                    return {"error": "File too large"}, 400
                await temp_file.write(chunk)
        
        # If we get here, file size is ok
        os.remove(temp_file_path)
        
        # Reset file position
        await file.seek(0)
        
        # Generate secure filename
        secure_name = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, secure_name)
        
        # Save the file
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(chunk_size):
                await out_file.write(chunk)
        
        # Return the file URL
        file_url = f"/static/uploads/{secure_name}"
        file = upload_to_gemini(file_path)
        wait_for_files_active([file])
        file_db[file_url] = file
        return {"url": file_url}

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {"error": "Upload failed"}, 500

@app.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    try:
        total_size = 0
        uploaded_files = []
        
        # First pass: check total size
        for file in files:
            file_size = 0
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    return {"error": "Total files size exceeds 25MB"}, 400
            await file.seek(0)
        
        # Second pass: save files
        for file in files:
            if not is_allowed_file(file.filename):
                continue
                
            secure_name = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, secure_name)
            
            async with aiofiles.open(file_path, 'wb') as out_file:
                while chunk := await file.read(1024 * 1024):
                    await out_file.write(chunk)
            
            uploaded_files.append(f"/static/uploads/{secure_name}")
        
        return {"urls": uploaded_files}

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {"error": "Upload failed"}, 500

# Add cleanup route (optional, for maintenance)
@app.post("/cleanup-uploads")
async def cleanup_uploads(request: Request):
    if "user" not in request.session:
        return {"error": "Unauthorized"}, 401
        
    try:
        # Delete files older than 24 hours
        current_time = datetime.now()
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (current_time - file_modified).days >= 1:
                os.remove(file_path)
        return {"message": "Cleanup successful"}
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        return {"error": "Cleanup failed"}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8300)
