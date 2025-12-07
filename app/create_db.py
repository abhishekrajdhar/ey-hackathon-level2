# create_db.py
from app.db.session import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)
