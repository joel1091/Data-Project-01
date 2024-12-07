import os
import subprocess
import sys
import time
import psycopg2
from psycopg2 import sql

# Ruta del archivo de configuración
CONFIG_FILE = "config.py"
REQUIREMENTS_FILE = "requirements.txt"

def install_requirements():
    """Instala las dependencias listadas en requirements.txt."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"No se encontró {REQUIREMENTS_FILE}. Asegúrate de que el archivo existe.")
        return

    print("Instalando dependencias desde requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
        print("Dependencias instaladas correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar dependencias: {e}")
        sys.exit(1)

def load_config():
    """Carga las credenciales desde el archivo config.py."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {CONFIG_FILE}")
    
    # Importar el archivo config.py como un módulo
    import config
    required_keys = ["host", "port", "database", "user", "password"]
    
    # Validar que todas las claves necesarias están presentes
    for key in required_keys:
        if not hasattr(config, key):
            raise KeyError(f"Falta la clave requerida '{key}' en el archivo config.py.")
    
    # Crear un diccionario con las credenciales
    return {
        "host": config.host,
        "port": config.port,
        "database": config.database,
        "user": config.user,
        "password": config.password,
    }

def wait_for_postgres(config, retries=10, delay=5):
    """Reintenta conectarse a PostgreSQL hasta que esté listo."""
    for attempt in range(retries):
        try:
            print(f"Intentando conectar a PostgreSQL (intento {attempt + 1}/{retries})...")
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                user=config["user"],
                password=config["password"],
                database="postgres"  # Conexión inicial
            )
            conn.close()
            print("PostgreSQL está listo.")
            return
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL no está listo: {e}")
            time.sleep(delay)

    print("Error: PostgreSQL no estuvo listo a tiempo.")
    sys.exit(1)

def create_database_if_not_exists(config):
    """Crea la base de datos si no existe y habilita PostGIS."""
    wait_for_postgres(config)  # Espera hasta que PostgreSQL esté listo
    try:
        print("Conectando al servidor PostgreSQL...")
        connection = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database="postgres"  # Conexión inicial al servidor
        )
        connection.autocommit = True
        cursor = connection.cursor()
        print("Conexión establecida al servidor PostgreSQL.")

        # Verificar si la base de datos existe
        print(f"Verificando si la base de datos '{config['database']}' existe...")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config["database"],))
        exists = cursor.fetchone()

        if not exists:
            # Crear la base de datos
            print(f"La base de datos '{config['database']}' no existe. Creándola...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(config["database"])))
            print(f"Base de datos '{config['database']}' creada con éxito.")
        else:
            print(f"La base de datos '{config['database']}' ya existe.")

        cursor.close()
        connection.close()

        # Conectar a la base de datos creada para habilitar PostGIS
        print(f"Conectando a la base de datos '{config['database']}' para habilitar PostGIS...")
        db_connection = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"]
        )
        db_cursor = db_connection.cursor()

        # Habilitar PostGIS
        db_cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        db_connection.commit()
        print(f"Extensión PostGIS habilitada en la base de datos '{config['database']}'.")

        db_cursor.close()
        db_connection.close()

    except Exception as e:
        print(f"Error al verificar/crear la base de datos: {e}")
        sys.exit(1)

def execute_scripts(scripts_dir, config):
    """Ejecuta todos los archivos .py en el directorio especificado."""
    # Listar todos los archivos .py en la carpeta
    scripts = [f for f in os.listdir(scripts_dir) if f.endswith(".py")]
    
    if not scripts:
        print(f"No se encontraron scripts en el directorio: {scripts_dir}")
        return
    
    for script in scripts:
        script_path = os.path.join(scripts_dir, script)
        print(f"Ejecutando: {script_path}")
        
        # Pasar las credenciales como variables de entorno
        env = os.environ.copy()
        env.update({
            "DB_HOST": config["host"],
            "DB_PORT": str(config["port"]),
            "DB_NAME": config["database"],
            "DB_USER": config["user"],
            "DB_PASSWORD": config["password"]
        })
        
        # Ejecutar el script
        try:
            subprocess.run(["python", script_path], env=env, check=True)
            print(f"Ejecutado correctamente: {script}")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar {script}: {e}")

def main():
    try:
        # Cargar configuración
        print("Cargando configuración...")
        config = load_config()
        print("Configuración cargada con éxito.")

        # Crear la base de datos si no existe y habilitar PostGIS
        print("Verificando/creando la base de datos y habilitando PostGIS...")
        create_database_if_not_exists(config)

        # Directorio donde están los scripts
        scripts_dir = "datasets_subidos"

        # Ejecutar los scripts
        print(f"Ejecutando scripts desde el directorio: {scripts_dir}")
        execute_scripts(scripts_dir, config)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
