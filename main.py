import os
import json
import yaml
import csv
import re
import logging
from datetime import datetime
import time


def setup_logger():
    logs_dir = './.logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_filename = datetime.now().strftime("log-%Y-%m-%d-%H-%M-%S.txt")
    log_filepath = os.path.join(logs_dir, log_filename)
    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.info("Logger setup complete.")


def log_message(message):
    logging.info(message)


def create_folder_structure(parent_directory, structure, variables):
    folder_count = 0
    for key, value in structure.items():
        if isinstance(value, dict) and key.startswith('folder'):
            new_folder_name = value.get('name', key)
            new_folder_name = new_folder_name.replace('$(foldername=', '{').replace(')', '}')
            keys = re.findall(r'{(\w+)}', new_folder_name)
            if not all(key in variables for key in keys):
                log_message(f"Missing values for {', '.join(key for key in keys if key not in variables)} in variables.")
                continue
            new_folder_name = new_folder_name.format(**variables)
            condition = value.get('condition')
            if condition:
                condition = condition.replace('$(condition=', '{').replace(')', '}')
                condition = condition.format(**variables)
                if str(condition).lower() not in ['true', '1']:
                    continue
            new_path = os.path.join(parent_directory, new_folder_name)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                log_message(f"Folder '{new_folder_name}' created successfully in '{parent_directory}'.")
                folder_count += 1
            sub_structure = {k: v for k, v in value.items() if k.startswith('folder')}
            if sub_structure:
                folder_count += create_folder_structure(new_path, sub_structure, variables)
    return folder_count


def load_settings():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            log_message("Read settings from 'settings.json'.")
    except FileNotFoundError:
        default_settings = {
            "creation_directory": "./Test/",
            "template_path": "./template.yml",
            "csv_path": "./variables.csv"
        }
        with open('settings.json', 'w') as f:
            json.dump(default_settings, f)
            log_message("Created default 'settings.json'.")
        settings = load_settings()
    return settings


def load_template(template_path):
    try:
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
            log_message(f"Read template from '{template_path}'.")
    except FileNotFoundError:
        default_template = {
            "folder1": {
                "name": "$(foldername=customer)",
                "folder1": {
                    "name": "Documentations",
                    "folder1": {
                        "name": "WIP"
                    }
                },
                "folder2": {
                    "name": "Releases",
                    "condition": "$(condition=release)"
                }
            }
        }
        with open(template_path, 'w') as f:
            yaml.dump(default_template, f)
            log_message(f"Created default template at '{template_path}'.")
        template = load_template(template_path)
    return template


def extract_variables(template):
    variables = set()
    template_str = str(template)
    matches = re.findall(r'\$\(([^)]+)\)', template_str)
    for match in matches:
        var_type, var_name = match.split('=')
        variables.add((var_name.strip(), var_type.strip()))
    return variables


def create_default_csv(csv_path, variables):
    default_row = {f'{var[0]}': '' if var[1] == 'foldername' else False for var in variables}
    with open(csv_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=default_row.keys())
        writer.writeheader()
    log_message(f"Created default CSV at '{csv_path}' with {len(default_row)} columns.")


def load_csv(csv_path, template):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    variables = extract_variables(template)
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            log_message(f"Read {len(rows)} rows and {len(rows[0]) if rows else 0} columns from '{csv_path}'.")
            missing_columns = set(var[0] for var in variables) - set(rows[0].keys()) if rows else set(var[0] for var in variables)
            extra_columns = set(rows[0].keys()) - set(var[0] for var in variables) if rows else set()
            if missing_columns:
                log_message(f"CSV file is missing columns: {missing_columns}")
            if extra_columns:
                log_message(f"CSV file has extra columns: {extra_columns}")
    except FileNotFoundError:
        create_default_csv(csv_path, variables)
        rows = []
        for row in rows:
            rows.append({var[0]: row[f'{var[0]}'] for var in variables})
    return rows


def execute():
    start_time = time.time()
    settings = load_settings()
    creation_directory = settings['creation_directory']
    template_path = settings['template_path']
    csv_path = settings['csv_path']
    template = load_template(template_path)
    rows = load_csv(csv_path, template)
    total_folders_created = 0
    for row in rows:
        total_folders_created += create_folder_structure(creation_directory, template, row)
    end_time = time.time()
    log_message(
        f"Program finished. Created {total_folders_created} folders. Execution time: {end_time - start_time} seconds.")


if __name__ == "__main__":
    setup_logger()
    log_message("Program started.")
    try:
        execute()
    except Exception as e:
        log_message(f"An error occurred: {str(e)}")
