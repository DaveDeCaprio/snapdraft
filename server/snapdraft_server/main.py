import logging
import os
from pathlib import Path

import dspy
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from snapdraft_server.logging_setup import setup_logging
from snapdraft_server.services.base.snapdraft_mongo import SnapdraftMongo
from snapdraft_server.routes.app_setup import create_app

load_dotenv()
setup_logging()

llm = dspy.LM(model="gpt-4o", max_tokens=4096)
dspy.settings.configure(lm=llm)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "snapdraft"
mongo_client = SnapdraftMongo(AsyncIOMotorClient(MONGO_URI), DATABASE_NAME)

# Add CORS middleware to allow your frontend to access the API
origins = [
    "http://localhost:3000",  # Replace with the port your React app is running on
    "http://localhost:5173",  # Adjust as per your Vite setup
]

local_cache_dir = Path("output/local_cache")
local_cache_dir.mkdir(parents=True, exist_ok=True)
dspy_dir = Path("output/dspy")
dspy_dir.mkdir(parents=True, exist_ok=True)
app = create_app(
    origins, mongo_client, local_cache_dir=local_cache_dir, dspy_dir=dspy_dir
)

# Run with: poetry run uvicorn snapdraft_server.main:app --reload
