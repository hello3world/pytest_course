from fastapi import FastAPI

app = FastAPI()


@app.get("/user/{user_id}/profile")
def user_profile(user_id: int):
    return {"user_id": user_id, "profile": "UserProfileData"}


@app.get("/user/{user_id}/files")
def user_files(user_id: int):
    return {"user_id": user_id, "files": ["file1.txt", "file2.txt"]}


@app.get("/analytics/sales")
def analytics_sales():
    return {"sales": 1000}


@app.get("/analytics/stock")
def analytics_stock():
    return {"stock": 42}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
