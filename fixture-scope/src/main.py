from fastapi import FastAPI

app = FastAPI()


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# cmd for backend launch
# python fixture-scope/src/main.py