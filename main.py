import os
import shutil


def create_folder(parent_directory, new_folder_name):
    new_path = os.path.join(parent_directory, new_folder_name)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
        print(f"Folder '{new_folder_name}' created successfully in '{parent_directory}'.")
        return new_path
    else:
        print(f"Folder '{new_folder_name}' already exists in '{parent_directory}'.")
        return None


def get_folder_names(parent_directory):
    all_items = os.listdir(parent_directory)
    names = [item for item in all_items if os.path.isdir(os.path.join(parent_directory, item))]
    return names


def copy_template(template, destination_directory):
    shutil.copytree(template, destination_directory)


if __name__ == "__main__":
    creation_directory = "C:/"  # TODO change this to the directory you want to use
    directory = "C:/"  # TODO change this to the directory you want to use
    template_directory = "C:/"  # TODO change this to the directory you want to use
    folder_names = get_folder_names(directory)
    for folder_name in folder_names:
        new_folder_path = create_folder(creation_directory, folder_name)
        if new_folder_path:
            copy_template(template_directory, new_folder_path)
