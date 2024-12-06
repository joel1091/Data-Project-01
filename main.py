import os
import subprocess
import json

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

        # Directorio donde están los scripts
        scripts_dir = "datasets_subidos"

        # Ejecutar los scripts
        print(f"Ejecutando scripts desde el directorio: {scripts_dir}")
        execute_scripts(scripts_dir, config)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
