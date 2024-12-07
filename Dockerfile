# Usa una imagen base con Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar herramientas del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    --no-install-recommends

# Copiar el archivo de dependencias al directorio de trabajo
COPY requirements.txt ./

# Copiar todo el contenido de la aplicación al directorio de trabajo
COPY . ./  

# Instalar las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Establecer el comando de inicio
CMD ["python", "main.py"]

