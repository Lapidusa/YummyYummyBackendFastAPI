from fastapi import APIRouter, Request
import subprocess
router = APIRouter()
@router.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    repo = payload.get("repository", {}).get("name")

    if repo == "YummyYummyBackendFastAPI":
        subprocess.Popen(["/bin/bash", "/root/YummyYummyAll/YummyYummyBackendFastAPI/deploy_back.sh"])
    elif repo == "YummyYummyFrontendNuxt":
        subprocess.Popen(["/bin/bash", "/root/YummyYummyAll/YummyYummyFrontendNuxt/deploy_front.sh"])

    return {"status": f"Deploy for {repo} started"}
