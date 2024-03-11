import os
from pathlib import Path
import requests
from tqdm import tqdm
import importlib.metadata as metadata
import json
from packaging import version

#################################################################
#### LOAD PARAMS FROM confignew.json - REQUIRED FOR BRANDING ####
#################################################################
# STARTUP VARIABLE - Create "this_dir" variable as the current script directory
this_dir = Path(__file__).parent.resolve()


# load standard config file in and get settings
def load_config(file_path):
    with open(file_path, "r") as config_file:
        config = json.load(config_file)
    return config


config_file_path = this_dir / "confignew.json"
params = load_config(config_file_path)

# Define the path to the modeldownload config file file
modeldownload_config_file_path = this_dir / "modeldownload.json"

# Check if the JSON file exists
if modeldownload_config_file_path.exists():
    with open(modeldownload_config_file_path, "r") as config_file:
        settings = json.load(config_file)

    # Extract settings from the loaded JSON
    base_path = Path(settings.get("base_path", ""))
    model_path = Path(settings.get("model_path", ""))
    files_to_download = settings.get("files_to_download", {})
else:
    # Default settings if the JSON file doesn't exist or is empty
    print(
        f"[{params['branding']}Startup] \033[91mWarning\033[0m modeldownload.json is missing so please re-download it and save it in the coquii_tts main folder."
    )
    print(
        f"[{params['branding']}Startup] \033[91mWarning\033[0m API Local and XTTSv2 Local will error unless this is corrected."
    )

# Read the version specifier from requirements_nvidia.txt
with open(this_dir / "requirements_nvidia.txt", "r") as req_file:
    requirements = req_file.readlines()

tts_version_required = None
for req in requirements:
    if req.startswith("TTS>="):
        tts_version_required = req.strip().split(">=")[1]
        break

if tts_version_required is None:
    raise ValueError(
        f"[{params['branding']}Startup] \033[91mWarning\033[0m Could not find TTS version specifier in requirements_nvidia.txt"
    )


def create_directory_if_not_exists(directory):
    if not directory.exists():
        directory.mkdir(parents=True)


def download_file(url, destination):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte

    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)

    with open(destination, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()


def check_tts_version():
    try:
        tts_version = metadata.version("tts")
        print(
            f"[{params['branding']}Startup] TTS version installed: \033[93m"
            + tts_version
            + "\033[0m"
        )

        if version.parse(tts_version) < version.parse(tts_version_required):
            print(
                f"[{params['branding']}Startup] \033[91mWarning\033[0m TTS version is too old. Please upgrade to version \033[93m"
                + tts_version_required
                + "\033[0m or later.\033[0m"
            )
            print(
                f"[{params['branding']}Startup] \033[91mWarning\033[0m At your terminal/command prompt \033[94mpip install --upgrade tts\033[0m"
            )
        else:
            print(f"[{params['branding']}Startup] TTS version is up to date.")
    except metadata.PackageNotFoundError:
        print(
            f"[{params['branding']}Startup] \033[91mWarning\033[0m TTS is not installed."
        )


# Check and create directories
if str(base_path) == "models":
    create_directory_if_not_exists(this_dir / base_path / model_path)
else:
    create_directory_if_not_exists(base_path / model_path)
    print(
        f"[{params['branding']}Startup] \033[94mInfo\033[0m Custom path set in \033[93mmodeldownload.json\033[0m. Using the following settings:"
    )
    print(
        f"[{params['branding']}Startup] \033[94mInfo\033[0m Base folder Path:\033[93m",
        base_path,
        "\033[0m",
    )
    print(
        f"[{params['branding']}Startup] \033[94mInfo\033[0m Model folder Path:\033[93m",
        model_path,
        "\033[0m",
    )
    print(
        f"[{params['branding']}Startup] \033[94mInfo\033[0m Full Path:\033[93m",
        base_path / model_path,
        "\033[0m",
    )

# Download files if they don't exist
print("[" + params["branding"] + "Startup] Checking Model is Downloaded.")
for filename, url in files_to_download.items():
    if str(base_path) == "models":
        destination = this_dir / base_path / model_path / filename
    else:
        destination = Path(base_path) / model_path / filename

    if not destination.exists():
        print(f"[{params['branding']}Startup] Downloading " + filename + "...")
        download_file(url, destination)

check_tts_version()
