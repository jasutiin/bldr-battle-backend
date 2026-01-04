from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

try:
  database_url: str = os.environ["SUPABASE_CONNECTION_STRING"]
except KeyError:
  print("ERROR: SUPABASE_CONNECTION_STRING environment variable is not set.")
  exit(1)

engine = create_engine(database_url)