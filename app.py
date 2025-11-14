from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pdfplumber
import os

app = FastAPI()

# Создаем папку для шаблонов
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "text": ""})

@app.post("/", response_class=HTMLResponse)
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    text = ""
    
    if file.filename.endswith('.pdf'):
        try:
            # Сохраняем временный файл
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            # Читаем PDF
            full_text = ""
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    full_text += f"--- Страница {page_num + 1} ---\n"
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n\n"
                    else:
                        full_text += "[Текст не найден]\n\n"
            
            text = full_text
            
            # Удаляем временный файл
            os.remove(file_path)
            
        except Exception as e:
            text = f"Ошибка: {str(e)}"
    
    return templates.TemplateResponse("index.html", {"request": request, "text": text})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)