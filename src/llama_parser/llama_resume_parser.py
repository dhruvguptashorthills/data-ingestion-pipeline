import os
import json
from pathlib import Path
from dotenv import load_dotenv
from llama_parse import LlamaParse
import fitz  # PyMuPDF
 
class ResumeParser:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
 
        if not api_key:
            raise ValueError("❌ LLAMA_CLOUD_API_KEY is missing from .env")
 
        self.parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",
            do_not_unroll_columns=True
        )
        self.RESUME_DIR = Path("data/resumes")
        self.OUTPUT_DIR = Path("data/llama_parse_resumes")
        self.SUPPORTED_EXTENSIONS = [".pdf", ".docx"]
 
    def extract_links_with_fitz(self, file_path):
        links = []
        try:
            with fitz.open(file_path) as doc:
                for page_number, page in enumerate(doc, start=1):
                    for link in page.get_links():
                        if "uri" in link:
                            links.append({
                                "text": page.get_textbox(link["from"]).strip(),
                                "uri": link["uri"]
                            })
        except Exception as e:
            print(f"⚠️ Failed to extract links from {file_path.name}: {e}")
        return links
 
    def parse_resume(self, file_path):
        try:
            documents = self.parser.load_data(file_path)
            combined_text = "\n".join([doc.text for doc in documents])
            parsed = {
                "file": file_path.name,
                "content": combined_text
            }
            if file_path.suffix.lower() == ".pdf":
                parsed["links"] = self.extract_links_with_fitz(file_path)
            return parsed
        except Exception as e:
            print(f"❌ Failed to parse {file_path.name}: {e}")
            return None
 
    def save_to_json(self, data, output_path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
 
    def run(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        resume_files = [f for f in self.RESUME_DIR.iterdir() if f.suffix.lower() in self.SUPPORTED_EXTENSIONS]
        print(f"🔍 Found {len(resume_files)} resume files to process.\n")
 
        for resume in resume_files:
            output_path = self.OUTPUT_DIR / f"{resume.stem}.json"
            if output_path.exists():
                print(f"⏩ Skipping {resume.name} (already processed)")
                continue
 
            print(f"📄 Processing: {resume.name}")
            parsed_data = self.parse_resume(resume)
            if parsed_data:
                self.save_to_json(parsed_data, output_path)
                print(f"✅ Saved: {output_path.name}")
            print("-" * 40)
 
 
if __name__ == "__main__":
    ResumeParser().run()