import os
import subprocess
from setuptools import setup
from setuptools.command.install import install

class CustomInstallCommand(install):
    def run(self):
        # Step 1: Install the dependencies from requirements.txt
        print("Installing dependencies from requirements.txt...")
        subprocess.check_call([os.sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

        # Step 2: Run the default install command to complete package installation
        install.run(self)

        # Step 3: Download necessary CSV files using gdown
        print("Downloading necessary CSV files...")

        imdb_data = '1yOjCi06k6hwkyfjk3ybZYXYAW2G9zrLR'
        pop_entries = '1NDxhsmy6K-hJNwqTIXe4gu-Yb5a-hpyJ'
        top_500_entries = '1nvkx2ZXcVgKQSrYZdB_PxROICivYrp4c'
        pop_films = '1LSoltimu-XVLqAIFl4QSUs-p02qhZiK8'

        file_urls = [
            {"url": f'https://drive.google.com/uc?export=download&id={imdb_data}', "filename": "imdb_data.csv"},
            {"url": f'https://drive.google.com/uc?export=download&id={pop_entries}', "filename": "pop_entries.csv"},
            {"url": f'https://drive.google.com/uc?export=download&id={top_500_entries}', "filename": "top_500_entries.csv"},
            {"url": f'https://drive.google.com/uc?export=download&id={pop_films}', "filename": "pop_films.csv"}
        ]

        # Create 'data' directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')

        # Download each file using gdown
        for file in file_urls:
            file_path = os.path.join('data', file["filename"])

            # Check if the file already exists
            if not os.path.exists(file_path):
                print(f"Downloading {file['filename']}...")
                import gdown  # Import gdown here, not at the top of the script
                gdown.download(file["url"], file_path, quiet=False)
            else:
                print(f"{file['filename']} already exists.")

# Setup configuration
setup(
    name="IMDb database exploration",  
    version="0.1",
    install_requires=[],  # No need to include gdown here since it's in requirements.txt
    cmdclass={'install': CustomInstallCommand},
)
