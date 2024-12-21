import os
import subprocess
from setuptools import setup
from setuptools.command.install import install
import s3fs


class CustomInstallCommand(install):
    def run(self):
        print("Installing dependencies from requirements.txt...")
        subprocess.check_call(
            [os.sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )

        install.run(self)

        print("Downloading necessary CSV files...")

        MY_BUCKET = "keithmoon"
        fs = s3fs.S3FileSystem(
            client_kwargs={"endpoint_url": "https://minio.lab.sspcloud.fr"}
        )
        files_url = f"{MY_BUCKET}/diffusion/data/"

        fs.get(f"{MY_BUCKET}/diffusion/data/", "data/", recursive=True)


# Setup configuration
setup(
    name="IMDb database exploration",
    version="0.1",
    install_requires=[],
    cmdclass={"install": CustomInstallCommand},
)
