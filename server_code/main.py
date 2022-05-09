import uvicorn
from fastapi import File, UploadFile, FastAPI, Response
from typing import List
from secrets import token_urlsafe  # for generating a nonce
import uuid
from prediction_utils import IrisPredictor
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import faulthandler

faulthandler.enable()

iris_predictors = dict()
app = FastAPI()

def save_file(fname, data):
    with open(fname, 'wb') as f:
        f.write(data)
    print(fname,'saved on server')
    
async def read_encrypted_text(file:UploadFile):
    # encoding = 2 stands for floats
    file_content = await file.read()
    return PyCtxt(serialized=file_content,encoding=2)

@app.get("/predict_encrypted/iris/info")
async def predict_iris_info():
    return "negative value corresponds to setosa and positive corresponds to versicolor"

@app.get("/predict_encrypted_perceptron/iris/info")
async def predict_iris_perceptron_info():
    return "value less than 0.5 corresponds to setosa and greater than 0.5 corresponds to versicolor"
    
@app.post("/predict_encrypted/iris/{uid}")
async def predict_iris(
    uid: str,
    sepal_length: UploadFile,sepal_width: UploadFile,
    petal_length: UploadFile,petal_width: UploadFile,
):
    global iris_predictors
    predictor = iris_predictors.get(uid)
    if predictor is None:
        predictor = IrisPredictor()
        predictor.load_session_key(uid)
        iris_predictors[uid] = predictor
        
    sepal_length_ctxt = await read_encrypted_text(sepal_length)
    sepal_width_ctxt = await read_encrypted_text(sepal_width)
    petal_length_ctxt = await read_encrypted_text(petal_length)
    petal_width_ctxt = await read_encrypted_text(petal_width)
    
    encrypted_ans = predictor.predict(
        sepal_length_ctxt,sepal_width_ctxt,petal_length_ctxt,petal_width_ctxt
    )
    return Response(content=encrypted_ans)

@app.post("/predict_encrypted_perceptron/iris/{uid}")
async def predict_iris_perceptron(
    uid: str,
    sepal_length: UploadFile,sepal_width: UploadFile,
    petal_length: UploadFile,petal_width: UploadFile,
):
    global iris_predictors
    predictor = iris_predictors.get(uid)
    if predictor is None:
        predictor = IrisPredictor()
        predictor.load_session_key(uid)
        iris_predictors[uid] = predictor
        
    sepal_length_ctxt = await read_encrypted_text(sepal_length)
    sepal_width_ctxt = await read_encrypted_text(sepal_width)
    petal_length_ctxt = await read_encrypted_text(petal_length)
    petal_width_ctxt = await read_encrypted_text(petal_width)
    
    encrypted_ans = predictor.predict_perceptron(
        sepal_length_ctxt,sepal_width_ctxt,petal_length_ctxt,petal_width_ctxt
    )
    return Response(content=encrypted_ans)
    
@app.post("/register_key")
async def upload(context: UploadFile = None,public_key: UploadFile = None,relin_key: UploadFile = None):
    uid = str(uuid.uuid4())
    print('registering new key',uid)
    # in case you need the files saved, once they are uploaded
    context_content = await context.read()
    save_file(f'{uid}.context',context_content)
    public_key_content = await public_key.read()
    save_file(f'{uid}.public_key',public_key_content)
    relin_key_content = await relin_key.read()
    save_file(f'{uid}.relin_key',public_key_content)

    return {"unique_id":uid}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080, debug=True)