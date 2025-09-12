# cli.py
import time

import keyring
import requests
import typer

app = typer.Typer()
API_BASE = "http://localhost:8000"
SERVICE = "repo-god"


@app.command()
def login(username: str = typer.Option(..., prompt=True)):
    """Login with GitHub OAuth Device Flow."""
    # 1) Start device flow
    r = requests.post(f"{API_BASE}/auth/device/start")
    data = r.json()
    typer.echo(
        f"👉 Go to {data['verification_uri']} and enter code: {data['user_code']}"
    )

    # 2) Poll until success
    while True:
        poll = requests.get(
            f"{API_BASE}/auth/device/poll", params={"device_code": data["device_code"]}
        ).json()
        if poll["status"] == "success":
            token = poll["access_token"]
            keyring.set_password(SERVICE, username, token)
            typer.echo(f"✅ Logged in as {username}, token stored securely.")
            break
        else:
            time.sleep(data["interval"])


@app.command()
def whoami(username: str = typer.Option(..., prompt=True)):
    token = keyring.get_password(SERVICE, username)
    if token:
        typer.echo(f"🔑 Logged in as {username}. Token stored in system keyring.")
    else:
        typer.echo("❌ Not logged in.")


@app.command()
def logout(username: str = typer.Option(..., prompt=True)):
    keyring.delete_password(SERVICE, username)
    typer.echo(f"👋 Logged out {username}.")


if __name__ == "__main__":
    app()
