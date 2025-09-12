# server.py
import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

app = FastAPI()


class DeviceStartResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int


@app.post("/auth/device/start", response_model=DeviceStartResponse)
def start_device_flow():
    """Start GitHub Device Flow and return code for CLI."""
    r = requests.post(
        "https://github.com/login/device/code",
        data={"client_id": CLIENT_ID, "scope": "repo read:org"},
        headers={"Accept": "application/json"},
    )
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=r.text)
    return r.json()


@app.get("/auth/device/poll")
def poll_device_flow(device_code: str):
    """Poll GitHub until user finishes login."""
    r = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_secret": CLIENT_SECRET,
        },
        headers={"Accept": "application/json"},
    )
    data = r.json()
    if "error" in data:
        return {"status": "pending", "error": data["error"]}
    return {"status": "success", "access_token": data["access_token"]}
