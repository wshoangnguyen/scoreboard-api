import json, os, shutil, threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from gdrive_backup import backup_to_sheet, restore_from_sheet

app = FastAPI()

# CORS - cho phép frontend gọi từ mọi nguồn
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA_FILE = Path("/data/scoreboard.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

PASSWORD = "Vuiqua123!"
VN_TZ = timezone(timedelta(hours=7))

DEFAULT = {
    "teacherName": "",
    "students": []
}

def load():
    try:
        if DATA_FILE.exists():
            return json.loads(DATA_FILE.read_text())
    except: pass
    return json.loads(json.dumps(DEFAULT))

def save(data):
    tmp = str(DATA_FILE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)
    # Backup to Google Sheets in background (don't block response)
    threading.Thread(target=backup_to_sheet, args=(data,), daemon=True).start()

# ---------- Streak ----------
def update_streak(student):
    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")
    yesterday = (datetime.now(VN_TZ) - timedelta(days=1)).strftime("%Y-%m-%d")
    last = student.get("lastActive", "")
    streak = student.get("streak", 0) or 0

    if last == today:
        return  # already logged today, no change
    student["lastActive"] = today
    if last == yesterday:
        student["streak"] = streak + 1
    else:
        student["streak"] = 1

# ---------- Models ----------
class AuthReq(BaseModel): password: str
class StudentReq(BaseModel): id: str; name: str
class ScoreReq(BaseModel): studentId: str; delta: int
class LevelReq(BaseModel): studentId: str; skill: str; level: int; delta: int
class RenameReq(BaseModel): id: str; name: str
class AvatarReq(BaseModel): id: str; avatar: str

# ---------- API ----------
@app.post("/api/auth")
def auth(req: AuthReq):
    if req.password == PASSWORD:
        return {"ok": True}
    raise HTTPException(401, "Sai mật khẩu")

@app.get("/api/data")
def get_data():
    return load()

@app.post("/api/students")
def add_student(s: StudentReq):
    d = load()
    if any(x["id"] == s.id for x in d["students"]):
        raise HTTPException(400, "ID existed")
    d["students"].append({
        "id": s.id, "name": s.name, "avatar": "",
        "totalScore": 0,
        "writing": [0,0,0,0,0], "speaking": [0,0,0,0,0],
        "lastActive": "", "streak": 0
    })
    save(d)
    return {"ok": True}

@app.delete("/api/students/{sid}")
def del_student(sid: str):
    d = load()
    d["students"] = [x for x in d["students"] if x["id"] != sid]
    save(d)
    return {"ok": True}

@app.post("/api/score")
def update_score(u: ScoreReq):
    d = load()
    s = next((x for x in d["students"] if x["id"] == u.studentId), None)
    if not s:
        raise HTTPException(404, "Not found")
    s["totalScore"] = max(0, s["totalScore"] + u.delta)
    if u.delta > 0:
        update_streak(s)
    save(d)
    return {"ok": True, "newScore": s["totalScore"], "streak": s.get("streak", 0)}

@app.post("/api/level")
def update_level(u: LevelReq):
    d = load()
    s = next((x for x in d["students"] if x["id"] == u.studentId), None)
    if not s:
        raise HTTPException(404, "Not found")
    s[u.skill][u.level] = max(0, s[u.skill][u.level] + u.delta)
    if u.delta > 0:
        update_streak(s)
    save(d)
    return {"ok": True, "newVal": s[u.skill][u.level], "streak": s.get("streak", 0)}

@app.post("/api/rename")
def rename_student(r: RenameReq):
    d = load()
    s = next((x for x in d["students"] if x["id"] == r.id), None)
    if s:
        s["name"] = r.name
        save(d)
    return {"ok": True}

@app.post("/api/avatar")
def update_avatar(a: AvatarReq):
    d = load()
   s = next((x for x in d["students"] if x["id"] == a.id), None)
    if s:
        s["avatar"] = a.avatar
        save(d)
    return {"ok": True}

# Auto-restore from Google Sheets on startup if local file is empty/missing
@app.on_event("startup")
def startup_restore():
    try:
        d = load()
        if not d.get("students"):
            restored = restore_from_sheet()
            if restored and restored.get("students"):
                save(restored)
                print("[startup] Restored data from Google Sheets backup")
    except Exception as e:
        print(f"[startup] Restore error: {e}")

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}
