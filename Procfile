web: gunicorn app:app --bind 0.0.0.0:$PORT --worker-class eventlet --log-level info
release: python init_db.py
