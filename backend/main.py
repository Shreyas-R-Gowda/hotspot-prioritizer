from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, reports, analytics, votes

app = FastAPI(title="Citizen AI System API")

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:80",
    "http://localhost",
    "https://your-render-app.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(votes.router)
app.include_router(analytics.router)

@app.on_event("startup")
async def startup():
    # Create tables on startup (for MVP)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Uncomment to reset DB
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "Citizen AI System Backend is running"}
