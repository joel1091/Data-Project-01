# Usa una imagen base con Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar herramientas del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias al directorio de trabajo
COPY requirements.txt ./

# Instalar las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el contenido de la aplicación al directorio de trabajo
COPY . .

# Exponer el puerto predeterminado de Streamlit
EXPOSE 8501

# Cambiar a la carpeta `streamlit_final`, esperar 10 segundos y ejecutar Streamlit
CMD ["bash", "-c", "sleep 10 && cd /app/streamlit_final && streamlit run streamlit.py --server.port=8501 --server.address=0.0.0.0"]