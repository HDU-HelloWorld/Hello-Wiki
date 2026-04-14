import uvicorn

if __name__ == "__main__":
    # Import string is required for reload (spawns a child that imports the app).
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
