cd /root/YummyYummyAll/YummyYummyBackendFastAPI
git reset --hard HEAD
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
pm2 restart fastapi