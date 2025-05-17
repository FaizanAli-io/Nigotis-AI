git fetch
git pull origin
pkill -f 'ngrok|python3'
source .venv/bin/activate
uv pip install -r requirements.txt
nohup python3 nigotis/manage.py runserver 0.0.0.0:8000 &
nohup ngrok http --domain=one-urchin-ultimate.ngrok-free.app 8000 &