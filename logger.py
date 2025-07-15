# logger.py
import json
import os
from datetime import datetime
import uuid

LOG_FILE = "history.json"

def init_log_file():
    """Menginisialisasi file log jika belum ada."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f) # Inisialisasi dengan list kosong

def log_gemini_call(prompt: str, response: str, status: str, metadata: dict = None):
    """
    Mencatat detail panggilan Gemini ke file log.

    Args:
        prompt (str): Prompt yang dikirim ke Gemini.
        response (str): Respons yang diterima dari Gemini.
        status (str): Status panggilan (e.g., "SUCCESS", "FAILED").
        metadata (dict, optional): Metadata tambahan seperti error message. Defaults to None.
    """
    init_log_file() # Pastikan file log sudah ada

    log_entry = {
        "id": str(uuid.uuid4()), # ID unik untuk setiap panggilan
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "status": status,
        "metadata": metadata if metadata is not None else {}
    }

    try:
        with open(LOG_FILE, 'r+') as f:
            data = json.load(f)
            data.append(log_entry)
            f.seek(0) # Kembali ke awal file
            json.dump(data, f, indent=4)
            print(f"Log disimpan untuk panggilan Gemini: ID {log_entry['id']}")
    except Exception as e:
        print(f"Gagal menulis log ke {LOG_FILE}: {e}")

def get_gemini_history():
    """Membaca seluruh riwayat panggilan Gemini dari file log."""
    init_log_file()
    try:
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Gagal membaca riwayat dari {LOG_FILE}: {e}")
        return []