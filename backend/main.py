from fastapi import FastAPI
from pydantic import BaseModel
from models.predictor import predict_return

app = FastAPI()

class InputData(BaseModel):
    ticker: str
    days: int

@app.post("/predict")
def predict(data: InputData):
    result = predict_return(data.ticker, data.days)
    return {"prediction": result}

