from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.Llama_parser.llama_resume_parser import ResumeParser
from src.Standardizer.standardizer import ResumeStandardizer

app = FastAPI()


@app.post("/parse")
def parse_resumes():
    try:
        ResumeParser().run()  # ✅ Just call the class directly
        return JSONResponse(content={"message": "✅ Resume parsing complete"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"❌ Parsing failed: {str(e)}"}, status_code=500)


@app.post("/standardize")
async def standardize_resumes():
    try:
        await ResumeStandardizer().run()  # ✅ Await because it's an async method
        return JSONResponse(content={"message": "✅ Resume standardization complete"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"❌ Standardization failed: {str(e)}"}, status_code=500)
