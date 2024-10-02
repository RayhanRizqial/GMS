from fastapi import FastAPI, File, Request, UploadFile, Depends, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db, create_tables
from models import ModelConfiguration, fineTuning, VectorStore, SubVectorStore
from typing import List, Optional
import time
import io
from datetime import datetime
from io import BytesIO
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
import json
import os
import logging
import uuid
# Library Baru:
#line 15, 26


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key="sk-")

# openai.api_key = "sk-"
app = FastAPI()

templates = Jinja2Templates(directory="templates")

#create new table
create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# +++++++++++++++ GET START ++++++++++++++++++++
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



# +++++++++++++++ Endpoint Database ModelConfiguration START ++++++++++++++++++++ 
@app.get("/api/models")
async def get_models(db: Session = Depends(get_db)):
    models = db.query(ModelConfiguration).all()
    return [
        {
            "id": model.id,
            "modelId": model.modelId,
            "namaModel": model.namaModel,
            "Instruksi": model.Instruksi,
            "verFine_tuning": model.verFine_tuning,
            "temp": model.temp,
            "tanggal": model.tanggal
        }
        for model in models
    ]

@app.get("/model-config-set")
async def model_configuration(request: Request, id: int = Query(...), db: Session = Depends(get_db)):
    # Mengambil model dari database berdasarkan ID
    selected_model = db.query(ModelConfiguration).filter(ModelConfiguration.id == id).first()
    
    if not selected_model:
        return templates.TemplateResponse("model-not-found.html", {"request": request})
    
    # Kirim data model yang dipilih ke halaman
    return templates.TemplateResponse("model-config-set.html", {"request": request, "model": selected_model})

# Endpoint untuk menampilkan halaman edit model
@app.get("/model-config-set/{model_id}")
async def get_model_configuration(request: Request, model_id: int, db: Session = Depends(get_db)):
    model = db.query(ModelConfiguration).filter(ModelConfiguration.id == model_id).first()
    if not model:
        return {"error": "Model not found"}
    
    return templates.TemplateResponse("model-config-set.html", {"request": request, "model": model})

# POST Endpoint untuk handle update model
@app.post("/model-config-set/{model_id}")
async def update_model_configuration(
    request: Request,
    model_id: int,
    modelId: str = Form(...),
    namaModelFineTune: str = Form(...),
    instruksiModel: str = Form(...),
    fineTuningVersion: str = Form(...),
    vectorId: str = Form(...),
    temp: float = Form(...),
    db: Session = Depends(get_db)
):
    # Log untuk cek apakah request sampai
    form_data = await request.form()
    logging.info(f"Form data: {form_data}")
    
    # Cari model berdasarkan ID
    model = db.query(ModelConfiguration).filter(ModelConfiguration.id == model_id).first()
    
    if not model:
        return {"error": "Model not found"}

    # Update nilai model
    model.modelId = modelId
    model.namaModel = namaModelFineTune
    model.Instruksi = instruksiModel
    model.verFine_tuning = fineTuningVersion
    model.vectorId = vectorId
    model.temp = temp

    # Commit perubahan ke database
    db.commit()
    logging.info(f"Model ID {model_id} has been updated successfully")

    # Redirect ke halaman edit model lagi dengan model yang diupdate
    return RedirectResponse(url=f"/model-configuration", status_code=303)
# +++++++++++++++ Endpoint Database ModelConfiguration END ++++++++++++++++++++   


# +++++++++++++++ Endpoint Database fineTuning START ++++++++++++++++++++   
@app.get("/api/fine-tuning")
async def get_fine_tunings(db: Session = Depends(get_db)):
    fine_tunings = db.query(fineTuning).all()
    return [
        {
            "id": fine_tuning.id,
            "jobId": fine_tuning.namaSuffix,
            "namaSuffix": fine_tuning.namaSuffix,
            "deskripsi": fine_tuning.deskripsi,
            "dataset": fine_tuning.dataset,
            "epocs": fine_tuning.epocs,
            "date": fine_tuning.date
        }
        for fine_tuning in fine_tunings
    ]

@app.get("/api/fine-tuning/{fine_tuning_id}")
async def get_fine_tuning(fine_tuning_id: int, db: Session = Depends(get_db)):
    fine_tuning = db.query(fineTuning).filter(fineTuning.id == fine_tuning_id).first()
    if fine_tuning is None:
        raise HTTPException(status_code=404, detail="Fine-tuning not found")
    return {
        "id": fine_tuning.id,
        "jobId": fine_tuning.namaSuffix,
        "namaSuffix": fine_tuning.namaSuffix,
        "deskripsi": fine_tuning.deskripsi,
        "dataset": fine_tuning.dataset,
        "modelOutput": fine_tuning.modelOutput,
        "epocs": fine_tuning.epocs,
        "date": fine_tuning.date
    }

@app.get("/fine-tuning/get")
async def get_datasets(db: Session = Depends(get_db)):
    datasets = db.query(fineTuning).all()  # Ambil semua data dari tabel fineTuning
    return [{"id": dataset.id, "namaSuffix": dataset.namaSuffix} for dataset in datasets]

@app.get("/api/dataset/{model_id}")
async def get_dataset(model_id: int, db: Session = Depends(get_db)):
    dataset = db.query(fineTuning).filter(fineTuning.id == model_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"dataset": dataset.dataset}
# +++++++++++++++ Endpoint Database fineTuning END ++++++++++++++++++++        

# +++++++++++++++ Endpoint Database Vector Stores Get START ++++++++++++++++++++   
@app.get("/api/vector-stores")
async def get_vector_stores(db: Session = Depends(get_db)):
    vector_stores = db.query(VectorStore).all()
    return [
        {
            "id": vector_store.id,
            "vectorId": vector_store.vectorId,
            "namaVector": vector_store.namaVector,
            "deskripsi": vector_store.deskripsi,
            "date": vector_store.date
        }
        for vector_store in vector_stores
    ]

@app.get("/api/vector-stores/{vector_store_id}")
async def get_vector_store(vector_store_id: int, db: Session = Depends(get_db)):
    vector_store = db.query(VectorStore).filter(VectorStore.id == vector_store_id).first()
    if vector_store is None:
        raise HTTPException(status_code=404, detail="Vector store not found")
    return {
        "id": vector_store.id,
        "vectorId": vector_store.vectorId,
        "namaVector": vector_store.namaVector,
        "deskripsi": vector_store.deskripsi,
        "date": vector_store.date
    }

@app.get("/api/sub-vector-stores")
async def get_sub_vector_stores(vectorId: str, db: Session = Depends(get_db)):
    sub_vector_stores = db.query(SubVectorStore).filter(SubVectorStore.vectorId == vectorId).all()
    return [
        {
            "id": sub_vector_store.id,
            "vectorId": sub_vector_store.vectorId,
            "topik": sub_vector_store.topik,
            "deskripsi": sub_vector_store.deskripsi,
            "path": sub_vector_store.path,
            "filesId": sub_vector_store.filesId,
            "dataset": sub_vector_store.dataset,
            "date": sub_vector_store.date
        }
        for sub_vector_store in sub_vector_stores
    ]
# +++++++++++++++ Endpoint Database Vector Stores Get END ++++++++++++++++++++    
    
    
    
    
# Ngambil Page

#info-management
@app.get("/info-management")
def main(request: Request):
    return templates.TemplateResponse("info-management.html", {"request": request})

@app.get("/info-management/add")
def main(request: Request):
    return templates.TemplateResponse("info-management-add.html", {"request": request})

@app.get("/info-management/info")
def main(request: Request):
    return templates.TemplateResponse("info-management-info.html", {"request": request})

@app.get("/fine-tuning")
def main(request: Request):
    return templates.TemplateResponse("fine-tuning.html", {"request": request})

@app.get("/fine-tuning/add")
def main(request: Request):
    return templates.TemplateResponse("fine-tuning-add.html", {"request": request})

@app.get("/fine-tuning/info")
def main(request: Request):
    return templates.TemplateResponse("fine-tuning-info.html", {"request": request})

@app.get("/create-assistant")
def main(request: Request):
    return templates.TemplateResponse("create-assistant.html", {"request": request})

@app.get("/model-configuration")
def main(request: Request):
    return templates.TemplateResponse("model-configuration.html", {"request": request})

@app.get("/about")
def main(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/dashboard")
def main(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/tanya-nekobot")
def main(request: Request):
    return templates.TemplateResponse("tanyaNekobot.html", {"request": request})

@app.get("/home", response_class=HTMLResponse, tags=["home"])
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/vector-stores")
def main(request: Request):
    return templates.TemplateResponse("vector-stores.html", {"request": request})

@app.get("/vector-stores/add")
def main(request: Request):
    return templates.TemplateResponse("vector-stores-add.html", {"request": request})

@app.get("/vector-stores/sub/")
def main(request: Request):
    return templates.TemplateResponse("vector-stores-sub.html", {"request": request})
# +++++++++++++++ GET END ++++++++++++++++++++

# +++++++++++++++ Post Database Fine-Tuning Start ++++++++++++++++++++
@app.post("/submit-finetuning")
async def submit_finetuning(
    request: Request,
    jobId: str = Form(...),
    namaSuffix: str = Form(...),
    deskripsi: str = Form(...),
    dataset: str = Form(...),
    jsonlFile: UploadFile = File(None),
    epocs: int = Form(...),
    system: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Handle dataset either from file or input dialog
        if jsonlFile:  # If file is uploaded
            contents = await jsonlFile.read()  # Membaca isi file JSONL
            lines = contents.decode("utf-8").splitlines()  # Memisahkan setiap baris JSONL
            dataset = []  # List untuk menyimpan hasil

            for line in lines:
                data = json.loads(line)  # Parsing setiap baris JSON
                messages = data.get("messages", [])  # Mengambil key 'messages'

                # Mencari konten dari user dan assistant
                user_content = None
                assistant_content = None

                for message in messages:
                    if message["role"] == "user":
                        user_content = message["content"]  # Menyimpan pertanyaan user
                    elif message["role"] == "assistant":
                        assistant_content = message["content"]  # Menyimpan jawaban assistant

                if user_content and assistant_content:
                    dataset.append([user_content, assistant_content])
        else:  # If dataset is from input dialog
            form_data = await request.form()
            dataset = []
            dataset_count = 1
            while f"user_{dataset_count}" in form_data:
                user_text = form_data[f"user_{dataset_count}"]
                assistant_text = form_data[f"assistant_{dataset_count}"]
                dataset.append((user_text, assistant_text))
                dataset_count += 1

        # Create fine-tuning object
        new_finetune = fineTuning(
            jobId=jobId,
            namaSuffix=namaSuffix,
            deskripsi=deskripsi,
            dataset=dataset,
            epocs=epocs,
            modelOutput=system,
            date=datetime.now().date()  # Current date
        )

        # Add to database and commit
        db.add(new_finetune)
        db.commit()

        # Redirect ke halaman edit model lagi dengan model yang diupdate
        return RedirectResponse(url=f"/fine-tuning", status_code=303)
    
    except Exception as e:
        logging.error(f"Error occurred during submission: {e}", exc_info=True)
        return {"error": "An error occurred during the fine-tuning submission."}
# +++++++++++++++ Post Database Fine-Tuning End ++++++++++++++++++++



# +++++++++++++++ Post Database Vector Stores Start ++++++++++++++++++++ ## Oke ini so far so good aman timan titik aman timan
@app.post("/submit-vector-store")
async def submit_vector_store(
    request: Request,
    namaVector: str = Form(...),
    deskripsi: str = Form(...),
    # jsonlFile: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        vectorId = str(uuid.uuid4())
        vector_store = VectorStore(
            vectorId=vectorId,
            namaVector=namaVector,
            deskripsi=deskripsi,
            date=datetime.utcnow()
        )
        db.add(vector_store)

        dataset = []

        # if jsonlFile:
        #     contents = await jsonlFile.read()
        #     try:
        #         dataset = json.loads(contents.decode("utf-8"))
        #     except json.JSONDecodeError:
        #         return {"error": "Invalid JSON format in the file"}
        # else:
        #     form_data = await request.form()
        #     dataset_count = 1
        #     while f"user_{dataset_count}" in form_data:
        #         user_text = form_data[f"user_{dataset_count}"]
        #         assistant_text = form_data[f"assistant_{dataset_count}"]
        #         dataset.append({
        #             "user": user_text,
        #             "assistant": assistant_text
        #         })
        #         dataset_count += 1

        # if not dataset:
        #     return {"error": "No dataset provided"}

        db.commit()

        return {"status": "success", "message": "Data has been updated or created", "vectorId": vectorId}
    
    except Exception as e:
        logging.error(f"Error occurred during submission: {e}", exc_info=True)
        return {"error": "An error occurred during the vector store submission."}

@app.post("/upload-sub-vector")
async def upload_sub_vector(
    vectorId: str = Form(...),
    deskripsi: str = Form(''),
    dataset: str = Form(...),
    # jsonlFile: UploadFile = File(None), 
    db: Session = Depends(get_db)
):
    # Generate a UUID for filesId
    filesId = str(uuid.uuid4())

    # if jsonlFile:
    #     file_content = await jsonlFile.read()
    #     dataset_content = json.loads(file_content)
    # elif dataset:
    #     dataset_content = json.loads(dataset)
    # else:
    #     dataset_content = []

    new_sub_vector = SubVectorStore(
        vectorId=vectorId,
        filesId=filesId,
        deskripsi=deskripsi,
        # dataset=dataset_content,
        path=jsonlFile.filename if jsonlFile else None
    )

    db.add(new_sub_vector)
    db.commit()
    db.refresh(new_sub_vector)

    return {"message": "SubVectorStore created successfully", "subVectorId": new_sub_vector.id}

# +++++++++++++++ Post Database Vector Stores End ++++++++++++++++++++

# +++++++++++++++ Fine-Tuning Start ++++++++++++++++++++
# Upload File Endpoint
class FineTuningRequest(BaseModel):
    training_file: str
    model: str = "gpt-3.5-turbo-0125"
    suffix: str
    
@app.post("/upload-file/")
async def upload_training_file(file: UploadFile):
    try:
        # Save file temporarily
        temp_file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)

        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Upload file to OpenAI
        with open(temp_file_path, "rb") as file_obj:
            response = client.files.create(
                file=file_obj,
                purpose="fine-tune"
            )

        # Clean up the temporary file
        os.remove(temp_file_path)

        return {"file_id": response.id, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fine-tuning Endpoint
@app.post("/create-fine-tuning-job/")
async def create_fine_tuning_job(request: FineTuningRequest):
    try:
        response = client.fine_tuning.jobs.create(
            training_file=request.training_file,
            model=request.model,
            suffix=request.suffix  # Add this line
        )
        return {"job_id": response.id, "status": response.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Monitoring Fine-Tuning Job Status
@app.get("/fine-tuning-job/{job_id}")
async def get_fine_tuning_job_status(job_id: str):
    try:
        response = client.fine_tuning.jobs.retrieve(job_id)
        return {
            "job_id": response.id,
            "status": response.status,
            "fine_tuned_model": response.fine_tuned_model,
            "created_at": response.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list-fine-tuning-jobs")
async def list_fine_tuning_jobs(limit: int = 50):
    try:
        response = client.fine_tuning.jobs.list(limit=limit)
        return {
            "jobs": [
                {
                    "id": job.id,
                    "status": job.status,
                    "model": job.model,
                    "output_model": job.fine_tuned_model  # Add this line
                } for job in response.data
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# +++++++++++++++ Fine-Tuning END ++++++++++++++++++++

@app.post("/create-assistant/")
async def create_assistant(
    name: str = Form(...),
    instructions: str = Form(...),
    model: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        supported_extensions = [
            ".c", ".cpp", ".csv", ".docx", ".html", ".java", ".json", ".md", ".pdf", 
            ".php", ".pptx", ".py", ".rb", ".tex", ".txt", ".css", ".jpeg", ".jpg", 
            ".js", ".gif", ".png", ".tar", ".ts", ".xlsx", ".xml", ".zip"
        ]
        
        file_ids = []
        for file in files:
            filename = file.filename
            if not filename:
                raise HTTPException(status_code=400, detail="File name is missing.")
            
            ext = os.path.splitext(filename)[1].lower()
            if ext not in supported_extensions:
                raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Supported extensions are: {', '.join(supported_extensions)}.")
            
            file_content = await file.read()
            file_like_object = BytesIO(file_content)
            file_like_object.name = filename  # Set the filename metadata
            
            uploaded_file = client.files.create(
                file=file_like_object,
                purpose="assistants"
            )
            file_ids.append(uploaded_file.id)
            print(f"Uploaded file with ID: {uploaded_file.id}")  # Debugging line
        
        vector_store = client.beta.vector_stores.create(
            name=f"{name}_store"
        )
        print(f"Created vector store with ID: {vector_store.id}")  # Debugging line
        
        batch = client.beta.vector_stores.file_batches.create(
            vector_store_id=vector_store.id,
            file_ids=file_ids
        )
        print(f"Created file batch with ID: {batch.id}")  # Debugging line
        
        max_wait_time = 120
        start_time = time.time()
        while True:
            if time.time() - start_time > max_wait_time:
                raise HTTPException(status_code=500, detail="Vector store creation timed out")
            
            # Corrected retrieval method with both vector_store_id and batch_id
            batch_status = client.beta.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store.id, 
                batch_id=batch.id
            )
            if batch_status.status == "completed":
                break
            elif batch_status.status == "failed":
                raise HTTPException(status_code=500, detail="Vector store file batch processing failed")
            time.sleep(5)
        
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=[{"type": "file_search"}]
        )
        print(f"Created assistant with ID: {assistant.id}")  # Debugging line
        
        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        
        return {"message": "Assistant created successfully", "assistant_id": assistant.id, "vector_store_id": vector_store.id}
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        raise HTTPException(status_code=500, detail=str(e))
# +++++++++++++++ Assistent END ++++++++++++++++++++

# +++++++++++++++ CREATE Assistant START ++++++++++++++++++++
@app.post("/create-assistant-aja/")
async def create_assistant(
    name: str = Form(...),
    instructions: str = Form(...),
    model: str = Form(...),
    vector_store_id: str = Form(...)
):
    try:
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=[{"type": "file_search"}]
        )
        print(f"Created assistant with ID: {assistant.id}")  # Debugging line
        
        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        
        return {"message": "Assistant created successfully", "assistant_id": assistant.id, "vector_store_id": vector_store_id}
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        raise HTTPException(status_code=500, detail=str(e))
# +++++++++++++++ CREATE Assistant START ++++++++++++++++++++


# +++++++++++++++ CREATE Vector START ++++++++++++++++++++
@app.post("/create-vector-store/")
async def create_vector_store(
    name: str = Form(...),
    files: List[UploadFile] = File(...),
):
    try:
        supported_extensions = [
            ".c", ".cpp", ".csv", ".docx", ".html", ".java", ".json", ".md", ".pdf", 
            ".php", ".pptx", ".py", ".rb", ".tex", ".txt", ".css", ".jpeg", ".jpg", 
            ".js", ".gif", ".png", ".tar", ".ts", ".xlsx", ".xml", ".zip"
        ]
        
        file_ids = []
        for file in files:
            filename = file.filename
            if not filename:
                raise HTTPException(status_code=400, detail="File name is missing.")
            
            ext = os.path.splitext(filename)[1].lower()
            if ext not in supported_extensions:
                raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Supported extensions are: {', '.join(supported_extensions)}.")
            
            file_content = await file.read()
            file_like_object = BytesIO(file_content)
            file_like_object.name = filename  # Set the filename metadata
            
            uploaded_file = client.files.create(
                file=file_like_object,
                purpose="assistants"
            )
            file_ids.append(uploaded_file.id)
            print(f"Uploaded file with ID: {uploaded_file.id}")  # Debugging line
        
        vector_store = client.beta.vector_stores.create(
            name=f"{name}_store"
        )
        print(f"Created vector store with ID: {vector_store.id}")  # Debugging line
        
        batch = client.beta.vector_stores.file_batches.create(
            vector_store_id=vector_store.id,
            file_ids=file_ids
        )
        print(f"Created file batch with ID: {batch.id}")  # Debugging line
        
        max_wait_time = 120
        start_time = time.time()
        while True:
            if time.time() - start_time > max_wait_time:
                raise HTTPException(status_code=500, detail="Vector store creation timed out")
            
            batch_status = client.beta.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store.id, 
                batch_id=batch.id
            )
            if batch_status.status == "completed":
                break
            elif batch_status.status == "failed":
                raise HTTPException(status_code=500, detail="Vector store file batch processing failed")
            time.sleep(5)
        
        return {"message": "Vector store created successfully", "vector_store_id": vector_store.id}
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        raise HTTPException(status_code=500, detail=str(e))
# +++++++++++++++ CREATE Vector START ++++++++++++++++++++

# +++++++++++++++ ADD Vector START ++++++++++++++++++++
@app.post("/add-file-to-vector-store/")
async def add_file_to_vector_store(
    vector_store_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        supported_extensions = [
            ".c", ".cpp", ".csv", ".docx", ".html", ".java", ".json", ".md", ".pdf",
            ".php", ".pptx", ".py", ".rb", ".tex", ".txt", ".css", ".jpeg", ".jpg",
            ".js", ".gif", ".png", ".tar", ".ts", ".xlsx", ".xml", ".zip"
        ]
        
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="File name is missing.")
        
        ext = os.path.splitext(filename)[1].lower()
        if ext not in supported_extensions:
            raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Supported extensions are: {', '.join(supported_extensions)}.")
        
        file_content = await file.read()
        file_like_object = BytesIO(file_content)
        file_like_object.name = filename  # Set the filename metadata
        
        uploaded_file = client.files.create(
            file=file_like_object,
            purpose="assistants"
        )
        
        batch = client.beta.vector_stores.file_batches.create(
            vector_store_id=vector_store_id,
            file_ids=[uploaded_file.id]
        )
        
        max_wait_time = 120
        start_time = time.time()
        while True:
            if time.time() - start_time > max_wait_time:
                raise HTTPException(status_code=500, detail="File processing timed out")
            
            # Corrected retrieval method with both vector_store_id and batch_id
            batch_status = client.beta.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store_id, 
                batch_id=batch.id
            )
            if batch_status.status == "completed":
                break
            elif batch_status.status == "failed":
                raise HTTPException(status_code=500, detail="File processing failed")
            time.sleep(5)
        
        return {"message": "File added to vector store successfully", "file_id": uploaded_file.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# +++++++++++++++ Vector END ++++++++++++++++++++




@app.post("/send-message/exp")
async def send_message_exp(request: Request, user_message: str = Form(...)):
    try:
        # Send the user's message to GPT
        response = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:personal::A4nAeG4G",
            messages=[
                {
                    "role": "system",
                    "content": """
Kamu adalah sebuah robot FAQ yang tugasnya adalah menjawab semua pertanyaan dari user yang berkaitan dengan topik universitas yang disini adalah universitas telkom pada jurusan informatika...
                """,
                },
                {"role": "user", "content": user_message},
            ],
        )

        gpt_response = response.choices[0].message.content

        # Analyze the GPT response to determine the expression
        expression = "Senyum.png"  # Default expression
        if "maaf" in gpt_response.lower() or "tidak tahu" in gpt_response.lower():
            expression = "Sedih.png"
        elif "berhati-hati" in gpt_response.lower():
            expression = "Khawatir.png"
        elif "terkejut" in gpt_response.lower() or "oh" in gpt_response.lower():
            expression = "Kaget.png"
        elif "panik" in gpt_response.lower():
            expression = "Panik.png"
        elif "semangat" in gpt_response.lower() or "bisa!" in gpt_response.lower():
            expression = "Semangat.png"
        else:
            expression = "Bingung.png"

        return {"response": gpt_response, "expression": expression}
    except Exception as e:
        print(e)
        return {"error": str(e)}



@app.post("/send-message/")
async def send_message(
    user_message: str = Form(...),
    assistant_id: str = Form(...),
    thread_id: Optional[str] = Form(None)
):
    try:
        # Jika tidak ada thread_id, buat thread baru
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
        
        # Kirim pesan pengguna ke GPT
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        # Tunggu hingga run selesai
        max_wait_time = 300
        start_time = time.time()
        while run.status not in ["completed", "failed", "cancelled"]:
            if time.time() - start_time > max_wait_time:
                raise HTTPException(status_code=500, detail="Assistant run timed out")
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        
        if run.status != "completed":
            return {"error": f"Assistant run {run.status}"}
        
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_response = messages.data[0].content[0].text.value

        # Menentukan ekspresi berdasarkan respons GPT
        expression = "Senyum.png"  # Default expression
        if "maaf" in assistant_response.lower() or "tidak tahu" in assistant_response.lower():
            expression = "Sedih.png"
        elif "berhati-hati" in assistant_response.lower():
            expression = "Khawatir.png"
        elif "terkejut" in assistant_response.lower() or "oh" in assistant_response.lower():
            expression = "Kaget.png"
        elif "panik" in assistant_response.lower():
            expression = "Panik.png"
        elif "semangat" in assistant_response.lower() or "bisa!" in assistant_response.lower():
            expression = "Semangat.png"
        else:
            expression = "Bingung.png"

        return {"response": assistant_response, "expression": expression, "thread_id": thread_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))