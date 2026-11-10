import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

project_dir = Path(__file__).resolve().parent
python_exe = project_dir / ".venv" / "Scripts" / "python.exe"
url = "http://127.0.0.1:8000/docs"

process = subprocess.Popen(
    [
        str(python_exe),
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ],
    cwd=project_dir,
)

try:
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError(
                "FastAPI stopped. Check the terminal for errors."
            )

        try:
            with urlopen("http://127.0.0.1:8000/openapi.json", timeout=1):
                webbrowser.open(url)
                break
        except (URLError, TimeoutError, OSError):
            time.sleep(1)
    else:
        raise RuntimeError("FastAPI did not become ready within 60 seconds.")

    process.wait()

except KeyboardInterrupt:
    process.terminate()
    process.wait()