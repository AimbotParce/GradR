"""
Projects management screens.
"""

import os
import platform
import subprocess
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from ..database import get_async_session
from ..database.models import Delivery


def open_native_file_picker():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)  # Bring dialog to front
    file_path = filedialog.askopenfilename(
        title="Select Delivery File",
        filetypes=[("All Files", "*.*"), ("PDF files", "*.pdf"), ("ZIP files", "*.zip")],
    )
    root.destroy()
    if not file_path:
        return None
    file_name = Path(file_path).name
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    return {"file_name": file_name, "file_bytes": file_bytes}


async def view_delivery(delivery_id: int):
    async with get_async_session() as session:
        delivery = await session.get(Delivery, delivery_id)
        if not delivery:
            return

    temp_dir = Path(tempfile.gettempdir()) / "grading_app_previews"
    temp_dir.mkdir(exist_ok=True)

    file_path = temp_dir / delivery.file_name

    with open(file_path, "wb") as f:
        f.write(delivery.file_bytes)

    # Tell the OS to open it
    system = platform.system()
    if system == "Windows":
        os.startfile(file_path)  # Opens PDF in Acrobat/Edge, ZIP in Explorer
    elif system == "Darwin":  # macOS
        subprocess.run(["open", str(file_path)])
    else:  # Linux
        subprocess.run(["xdg-open", str(file_path)])
