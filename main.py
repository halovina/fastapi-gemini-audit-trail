# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from logger import log_gemini_call, get_gemini_history
from config import GEMINI_API_KEY
import os

# Konfigurasi Gemini API Key
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="Gemini Call Audit & Historicity API",
    description="Sistem logging komprehensif untuk panggilan Gemini, termasuk audit dan debugging.",
    version="1.0.0"
)

# Inisialisasi model Gemini
try:
    gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    print("Model Gemini berhasil diinisialisasi.")
except Exception as e:
    print(f"Error saat menginisialisasi model Gemini: {e}")
    # Anda mungkin ingin menangani ini lebih baik di produksi, misalnya dengan exit atau pesan error.

class PromptRequest(BaseModel):
    prompt: str

@app.post("/call-gemini/")
async def call_gemini_endpoint(request: PromptRequest):
    """
    Endpoint untuk mengirim prompt ke Gemini dan mencatat hasilnya.
    """
    user_prompt = request.prompt
    gemini_response = ""
    log_status = "SUCCESS"
    log_metadata = {}

    try:
        if not gemini_model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized.")

        # Kirim prompt ke Gemini
        response = gemini_model.generate_content(user_prompt)
        gemini_response = response.text
        print(f"Respon Gemini diterima: {gemini_response[:100]}...") # Log 100 karakter pertama

    except genai.types.BlockedPromptException as e:
        log_status = "BLOCKED"
        log_metadata = {"error": "Prompt diblokir oleh Gemini", "details": str(e)}
        gemini_response = "Prompt diblokir oleh Gemini karena alasan keamanan atau kebijakan."
        print(f"Prompt diblokir: {e}")
        raise HTTPException(status_code=400, detail=gemini_response)

    except Exception as e:
        log_status = "FAILED"
        log_metadata = {"error": str(e)}
        gemini_response = f"Terjadi kesalahan saat memanggil Gemini: {e}"
        print(f"Error saat memanggil Gemini: {e}")
        raise HTTPException(status_code=500, detail=gemini_response)

    finally:
        # Selalu log panggilan, terlepas dari sukses atau gagal
        log_gemini_call(
            prompt=user_prompt,
            response=gemini_response,
            status=log_status,
            metadata=log_metadata
        )

    return {"prompt": user_prompt, "response": gemini_response, "log_status": log_status}

@app.get("/gemini-history/")
async def get_history():
    """
    Endpoint untuk mendapatkan seluruh riwayat panggilan Gemini.
    """
    history = get_gemini_history()
    return {"history": history}

@app.get("/")
async def root():
    return {"message": "Selamat datang di Gemini Call Audit & Historicity API! Kunjungi /docs untuk dokumentasi API."}

