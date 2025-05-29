from fastapi import FastAPI, Request, Header, HTTPException
import hmac
import hashlib
import subprocess

app = FastAPI()
SECRET = b'my_webhook_secret'

@app.post("/github-webhook/")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()
    expected = 'sha256=' + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    subprocess.Popen(["/root/deploy.sh"])
    return {"status": "success"}
