import os
from config import GROQ_API_KEY, TAVILY_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from crewai import Crew, Process
from agents import researcher, analyst, writer, reviewer
from tasks import create_tasks
from export import generate_pdf, generate_docx
from database import save_research, get_research_history, save_pdf, get_pdf_library, get_settings, save_settings
from rag import process_pdf_with_rag
import time
import shutil
import asyncio

app = FastAPI(title="Multi-Agent Research Assistant")
templates = Jinja2Templates(directory="templates")
last_report = {"text": "", "query": ""}

@app.get("/ui")
async def ui(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/")
def home():
    return {"message": "Research Assistant is running!"}

@app.post("/research")
async def run_research(
    query: str = Form(...),
    pdf: UploadFile = File(None)
):
    start_time = time.time()
    pdf_content = ""

    try:
        if pdf and pdf.filename:
            pdf_path = f"temp_{pdf.filename}"
            with open(pdf_path, "wb") as f:
                shutil.copyfileobj(pdf.file, f)
            from tools import pdf_tool
            raw_pdf = pdf_tool.run(pdf_path)
            pdf_content = process_pdf_with_rag(raw_pdf, query)
            save_pdf(pdf.filename, raw_pdf)
            os.remove(pdf_path)

        tasks = create_tasks(query, pdf_content)

        crew = Crew(
            agents=[researcher, analyst, writer, reviewer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        result = await asyncio.to_thread(crew.kickoff)

        end_time = time.time()
        elapsed = round(end_time - start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        time_taken = f"{minutes}m {seconds}s"

        report_text = str(result)
        last_report["text"] = report_text
        last_report["query"] = query
        save_research(query, report_text, time_taken)

        return JSONResponse({
            "status": "completed",
            "query": query,
            "time_taken": time_taken,
            "report": report_text
        })

    except Exception as e:
        end_time = time.time()
        elapsed = round(end_time - start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return JSONResponse({
            "status": "error",
            "query": query,
            "time_taken": f"{minutes}m {seconds}s",
            "report": f"## Error\n\nSomething went wrong:\n\n{str(e)}\n\n**Try:**\n* A shorter or simpler query\n* Waiting 1 minute and trying again\n* A smaller PDF file"
        })

@app.get("/history")
def history():
    return JSONResponse(get_research_history())

@app.get("/pdfs")
def pdfs():
    return JSONResponse(get_pdf_library())

@app.get("/settings")
def settings():
    return JSONResponse(get_settings())

@app.post("/settings")
async def update_settings(request: Request):
    data = await request.json()
    save_settings(data)
    return JSONResponse({"status": "saved"})

@app.get("/history/{id}")
def get_report(id: int):
    history = get_research_history()
    for item in history:
        if item["id"] == id:
            last_report["text"] = item["report"]
            last_report["query"] = item["query"]
            return JSONResponse(item)
    return JSONResponse({"error": "Not found"}, status_code=404)

@app.get("/export/pdf")
async def export_pdf():
    if not last_report["text"]:
        return JSONResponse({"error": "No report to export"})
    buffer = generate_pdf(last_report["text"], last_report["query"])
    return StreamingResponse(buffer, media_type="application/pdf",
                           headers={"Content-Disposition": "attachment; filename=research_report.pdf"})

@app.get("/export/docx")
async def export_docx():
    if not last_report["text"]:
        return JSONResponse({"error": "No report to export"})
    buffer = generate_docx(last_report["text"], last_report["query"])
    return StreamingResponse(buffer,
                           media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           headers={"Content-Disposition": "attachment; filename=research_report.docx"})