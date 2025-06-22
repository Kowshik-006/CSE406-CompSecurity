import os

# Replace with your actual dataset path
dataset_slug = "kowshiksaha006/sca-dataset"
dataset_slug_merged = "kowshiksaha006/sca-dataset-merged"

# Download location
download_path = "./dataset"

os.makedirs(download_path, exist_ok=True)

# Command to download dataset
os.system(f"kaggle datasets download -d {dataset_slug} -p {download_path} --unzip")
os.system(f"kaggle datasets download -d {dataset_slug_merged} -p {download_path} --unzip")
