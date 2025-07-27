# Imagen base
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Copia de archivos
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando por defecto
CMD ["python", "app.py"]
