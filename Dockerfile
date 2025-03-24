FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ .  # Copy the rest of your backend code (api.py, utils, etc.)

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"] # HF Spaces expects app to run on port 7860