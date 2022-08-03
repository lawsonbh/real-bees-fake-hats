from fastapi import FastAPI


app = FastAPI()


@app.post("/bees/{file_path:path}")
def store_bee_photo(file_path: str):
    return {"file_path": file_path}

@app.get("/bees/{file_path:path}")
def fetch_bee_photo(file_path: str):
    return {"file_path": file_path}

@app.delete("/bees/{file_path:path}")
def delete_bee_photo(file_path: str):
    return {"file_path": file_path}