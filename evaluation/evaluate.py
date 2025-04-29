import os
import json
import pandas as pd
import re
import matplotlib.pyplot as plt

class ResumeEvaluator:
    def __init__(self, directory, output_file, report_file):
        self.directory = directory
        self.output_file = output_file
        self.report_file = report_file
        self.columns = [
            "Filename", "Name", "Email", "Phone", "Location", "Summary",
            "Education Degree", "Education Institution", "Education Year",
            "Experience Title", "Experience Company", "Experience Duration",
            "Experience Location", "Experience Description", "Skills",
            "Project Title", "Project Description", "Certifications",
            "Languages", "Social Profiles"
        ]
        self.filenames = self.get_filenames()
        self.data = self.initialize_data()

    def get_filenames(self):
        return sorted([f for f in os.listdir(self.directory) 
                       if os.path.isfile(os.path.join(self.directory, f)) and f.endswith(".json")])

    def initialize_data(self):
        data = {col: [""] * len(self.filenames) for col in self.columns}
        data["Filename"] = self.filenames
        return data

    @staticmethod
    def validate_email(email):
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))

    @staticmethod
    def validate_phone_number(phone_number):
        phone_pattern = re.compile(r'''
            ^                                # start
            ([A-Za-z]\s)?                    # optional single letter followed by space
            (\(?\+?\d{1,3}\)?[-.\u2013\s]*)? # optional country code, allowing – as sep
            (\(?\d{2,5}\)?[-.\u2013\s]*)?    # optional area code, allowing – as sep
            (                                # main number:
                (?:\d[-.\u2013\s]*){10}      # exactly 10 digits with optional separators
            )
            $                                # end
        ''', re.VERBOSE)
        phone_numbers = re.split(r'\s*[,/]\s*', phone_number)
        return all(phone_pattern.match(num.strip()) for num in phone_numbers)
    def process_file(self, filename, index):
        file_path = os.path.join(self.directory, filename)
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                self.map_fields(json_data, index)
        except (json.JSONDecodeError, KeyError):
            for col in self.columns[1:]:
                self.data[col][index] = "NULL"

    def map_fields(self, json_data, index):
        self.data["Name"][index] = "PRESENT" if json_data.get("name") else "NULL"
        
        # Validate email
        email = json_data.get("email", "")
        if email:
            self.data["Email"][index] = "PRESENT" if self.validate_email(email) else "INVALID PRESENT"
        else:
            self.data["Email"][index] = "NULL"
        
        # Validate phone
        phone = json_data.get("phone", "")
        if phone:
            self.data["Phone"][index] = "PRESENT" if self.validate_phone_number(phone) else "INVALID PRESENT"
        else:
            self.data["Phone"][index] = "NULL"
        
        self.data["Location"][index] = "PRESENT" if json_data.get("location") else "NULL"
        self.data["Summary"][index] = "PRESENT" if json_data.get("summary") else "NULL"
        
        # Check education details
        if "education" in json_data and json_data["education"]:
            education = json_data["education"][0]  # Take the first education entry
            self.data["Education Degree"][index] = "PRESENT" if education.get("degree") else "NULL"
            self.data["Education Institution"][index] = "PRESENT" if education.get("institution") else "NULL"
            self.data["Education Year"][index] = "PRESENT" if education.get("year") else "NULL"
        else:
            self.data["Education Degree"][index] = "NULL"
            self.data["Education Institution"][index] = "NULL"
            self.data["Education Year"][index] = "NULL"
        
        # Check experience details
        if "experience" in json_data and json_data["experience"]:
            experience = json_data["experience"][0]  # Take the first experience entry
            self.data["Experience Title"][index] = "PRESENT" if experience.get("title") else "NULL"
            self.data["Experience Company"][index] = "PRESENT" if experience.get("company") else "NULL"
            self.data["Experience Duration"][index] = "PRESENT" if experience.get("duration") else "NULL"
            self.data["Experience Location"][index] = "PRESENT" if experience.get("location") else "NULL"
            self.data["Experience Description"][index] = "PRESENT" if experience.get("description") else "NULL"
        else:
            self.data["Experience Title"][index] = "NULL"
            self.data["Experience Company"][index] = "NULL"
            self.data["Experience Duration"][index] = "NULL"
            self.data["Experience Location"][index] = "NULL"
            self.data["Experience Description"][index] = "NULL"
        
        # Check other fields
        self.data["Skills"][index] = "PRESENT" if json_data.get("skills") else "NULL"
        if "projects" in json_data and json_data["projects"]:
            project = json_data["projects"][0]  # Take the first project entry
            self.data["Project Title"][index] = "PRESENT" if project.get("title") else "NULL"
            self.data["Project Description"][index] = "PRESENT" if project.get("description") else "NULL"
        else:
            self.data["Project Title"][index] = "NULL"
            self.data["Project Description"][index] = "NULL"
        
        self.data["Certifications"][index] = "PRESENT" if json_data.get("certifications") else "NULL"
        self.data["Languages"][index] = "PRESENT" if json_data.get("languages") else "NULL"
        self.data["Social Profiles"][index] = "PRESENT" if json_data.get("social_profiles") else "NULL"

    def generate_dataframe(self):
        for i, filename in enumerate(self.filenames):
            self.process_file(filename, i)
        return pd.DataFrame(self.data)

    def save_dataframe(self, df):
        df.to_excel(self.output_file, index=False)

    def generate_report(self, df):
        total_rows = len(df)
        total_nulls = df.apply(lambda col: col.isin(["NULL"]).sum()).sum()
        invalid_phone_count = df["Phone"].isin(["INVALID PRESENT"]).sum()
        invalid_email_count = df["Email"].isin(["INVALID PRESENT"]).sum()
        specific_null_counts = {col: df[col].isin(["NULL"]).sum() for col in self.columns[1:]}
        report_data = {
            "Metric": ["Total Number of Entries", "Total Null Values", "Invalid Phone Numbers", "Invalid Email Addresses"] + list(specific_null_counts.keys()),
            "Details": [total_rows, total_nulls, invalid_phone_count, invalid_email_count] + list(specific_null_counts.values()),
        }
        report_df = pd.DataFrame(report_data)
        report_df.to_excel(self.report_file, index=False)

    def plot_chart(self):
        df = pd.read_excel(self.report_file)
        fields = df["Metric"].tolist()
        null_values = df["Details"].tolist()
        if "Total Null Values" in fields:
            index = fields.index("Total Null Values")
            fields.pop(index)
            null_values.pop(index)
        plt.figure(figsize=(12, 8))
        bars = plt.barh(fields, null_values, color='skyblue')
        plt.xlabel('Number of Values')
        plt.title('Values from Resume Field')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        for bar, value in zip(bars, null_values):
            plt.annotate(str(value), xy=(value, bar.get_y() + bar.get_height() / 2), xytext=(5, 0), textcoords="offset points", va='center', ha='left', fontsize=10)
        plt.savefig('evaluation/bar_chart.png')
        plt.show()

def main():
    directory = "/home/shtlp_0152/Desktop/project 1/data-ingestion-pipeline/data/standardized_resumes"
    output_file = "evaluation/evaluation.xlsx"
    report_file = "evaluation/data_quality_report.xlsx"
    evaluator = ResumeEvaluator(directory, output_file, report_file)
    df = evaluator.generate_dataframe()
    evaluator.save_dataframe(df)
    evaluator.generate_report(df)
    evaluator.plot_chart()

if __name__ == "__main__":
    main()