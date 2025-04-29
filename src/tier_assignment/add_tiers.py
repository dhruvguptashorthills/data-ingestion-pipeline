import os
import json
import csv
import numpy as np
from sentence_transformers import SentenceTransformer, util


class CollegeTierAssigner:
    ABBREVIATIONS = {
        "IIT": "Indian Institute of Technology",
        "BITS": "Birla Institute of Technology and Science"
    }

    def __init__(self, csv_path):
        self.college_tiers = self.load_college_tiers(csv_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.college_names = list(self.college_tiers.keys())
        self.college_embeddings = self.model.encode(self.college_names, convert_to_tensor=True, show_progress_bar=False)

    def load_college_tiers(self, csv_path):
        college_tiers = {}
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if 'Institution' not in reader.fieldnames or 'Tier' not in reader.fieldnames:
                raise ValueError("CSV must contain 'Institution' and 'Tier' columns")
            for row in reader:
                college_tiers[row['Institution'].strip()] = row['Tier'].strip()
        return college_tiers

    def expand_abbreviations(self, institution_name):
        for abbreviation, full_name in self.ABBREVIATIONS.items():
            institution_name = institution_name.replace(abbreviation, full_name)
        return institution_name

    def get_best_match(self, institution, threshold=0.8):
        if not institution:
            return None, None

        institution = self.expand_abbreviations(institution)

        if 'school' in institution.lower():
            print(f"Skipping '{institution}' as it contains 'school' in its name.")
            return None, None

        try:
            institution_embedding = self.model.encode(institution, convert_to_tensor=True)
            similarities = util.cos_sim(institution_embedding, self.college_embeddings)[0]
            best_idx = np.argmax(similarities)
            score = similarities[best_idx].item()
            matched_name = self.college_names[best_idx]
            print(f"Trying match: '{institution}' → '{matched_name}' (Score: {score*100:.2f})")

            if score >= threshold:
                return matched_name, self.college_tiers[matched_name]
            else:
                print(f"No match for '{institution}' (best match: '{matched_name}', score: {score*100:.2f})")
                return None, None

        except Exception as e:
            print(f"Error encoding institution '{institution}': {e}")
            return None, None


class ResumeProcessor:
    TIER1_CITIES = {
        "delhi", "new delhi", "gurgaon", "gurugram",
        "bangalore", "bengaluru", "hyderabad", "mumbai", "noida"
    }

    def __init__(self, resume_dir, output_dir, college_assigner, include_debug=True):
        self.resume_dir = resume_dir
        self.output_dir = output_dir
        self.college_assigner = college_assigner
        self.include_debug = include_debug

    def get_json_files(self):
        return sorted([f for f in os.listdir(self.resume_dir)
                       if os.path.isfile(os.path.join(self.resume_dir, f))])

    def get_location_tier(self, location):
        if not location:
            return "Tier2"
        location = location.lower().strip()
        for city in self.TIER1_CITIES:
            if city in location:
                return "Tier1"
        return "Tier2"

    def process_resumes(self):
        os.makedirs(self.output_dir, exist_ok=True)
        json_files = self.get_json_files()

        for file in json_files:
            resume_path = os.path.join(self.resume_dir, file)
            print(f"Processing file: {resume_path}")

            try:
                with open(resume_path, mode='r', encoding='utf-8') as f:
                    resume_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading {resume_path}: {e}")
                continue

            updated = False

            for edu in resume_data.get('education', []):
                institution = edu.get('institution', '').strip()
                if institution:
                    matched_name, tier = self.college_assigner.get_best_match(institution)
                    if tier:
                        edu['tier'] = tier
                        if self.include_debug:
                            edu['matched_institution'] = matched_name
                        updated = True
                    else:
                        edu['tier'] = 'Tier3'
                        if self.include_debug:
                            edu['matched_institution'] = 'No Match'
                        updated = True

            location = (resume_data.get('location') or '').strip()

            resume_data['location_tier'] = self.get_location_tier(location)
            updated = True

            try:
                relative_path = os.path.relpath(resume_path, self.resume_dir)
                output_path = os.path.join(self.output_dir, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, mode='w', encoding='utf-8') as f:
                    json.dump(resume_data, f, indent=4, ensure_ascii=False)
                print(f"{'✅ Updated' if updated else '❌ Skipped'}: {file}")
            except Exception as e:
                print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    csv_path = "/home/shtlp_0152/Desktop/project 1/data-ingestion-pipeline/src/tier_assignment/college_tiers.csv"
    resume_dir = "/home/shtlp_0152/Desktop/project 1/data-ingestion-pipeline/data/standardized_resumes"
    output_dir = "/home/shtlp_0152/Desktop/project 1/data-ingestion-pipeline/data/standardized_resumewithtierlevels"

    try:
        college_assigner = CollegeTierAssigner(csv_path)
        processor = ResumeProcessor(resume_dir, output_dir, college_assigner, include_debug=True)
        processor.process_resumes()
    except Exception as e:
        print(f"Script failed: {e}")
