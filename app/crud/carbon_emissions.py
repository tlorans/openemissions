import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.carbon_emissions import CarbonEmissionsModel


class CarbonEmissionsCRUD:
    @staticmethod
    def load_json_files(json_folder_path: str):
        json_files = [pos_json for pos_json in os.listdir(json_folder_path) if pos_json.endswith('.json')]
        data = []
        for file_name in json_files:
            parts = file_name.replace('.json', '').split('_')
            year = parts[-1]
            company_name = ' '.join(parts[:-1])
            with open(os.path.join(json_folder_path, file_name), 'r') as json_file:
                report = json.load(json_file)
                # first check if Scope 1, 2 and 3 are numeric values
                if all(isinstance(report[scope], (int, float)) for scope in ['Scope 1', 'Scope 2', 'Scope 3']):
                    data.append({
                        'name': company_name,
                        'year_published': int(year),
                        'scope_1': report['Scope 1'] if report['Scope 1'] != 0 else None,
                        'scope_2': report['Scope 2'] if report['Scope 2'] != 0 else None,
                        'scope_3': report['Scope 3'] if report['Scope 3'] != 0 else None,
                    })
                else:
                    print(f"Invalid data for {company_name} in {year}")
        return data

    @staticmethod
    def save_to_db(db: Session, data: list):
        for entry in data:
            # Check if the record already exists
            existing_record = db.query(CarbonEmissionsModel).filter(
                CarbonEmissionsModel.name == entry['name'],
                CarbonEmissionsModel.year_published == entry['year_published']
            ).first()
            if not existing_record:
                carbon_emission = CarbonEmissionsModel(
                    name=entry['name'],
                    year_published=entry['year_published'],
                    scope_1=entry['scope_1'],
                    scope_2=entry['scope_2'],
                    scope_3=entry['scope_3']
                )
                db.add(carbon_emission)
        db.commit()
