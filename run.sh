git fetch
git pull origin

nohup python3 nigotis/manage.py runserver 0.0.0.0:8000 &
nohup ngrok http --domain=one-urchin-ultimate.ngrok-free.app 8000 &