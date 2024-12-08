import os
import ast

def get_imported_libraries_from_file(filepath):
    """Obtiene las librerías importadas desde un archivo Python"""
    libraries = set()
    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read(), filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        libraries.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        libraries.add(node.module.split('.')[0])
        except Exception as e:
            print(f"Error analizando {filepath}: {e}")
    return libraries

def get_imported_libraries_from_project(project_path):
    """Obtiene las librerías importadas desde todos los archivos .py de un proyecto"""
    all_libraries = set()
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                libraries = get_imported_libraries_from_file(filepath)
                all_libraries.update(libraries)
    return all_libraries

def filter_standard_libraries(libraries):
    """Filtra las librerías de la biblioteca estándar de Python"""
    standard_libraries = {'os', 'sys', 'json', 're', 'time', 'random', 'math', 'datetime', 'itertools', 'collections', 'functools', 
                          'string', 'unittest', 'subprocess', 'traceback', 'argparse', 'shutil', 'statistics', 'dataclasses', 
                          'pathlib', 'asyncio', 'concurrent', 'pdb', 'typing', 'importlib', 'warnings'}
    return libraries - standard_libraries

if __name__ == "__main__":
    # Directorio del proyecto (puedes cambiar esta ruta)
    project_path = os.path.abspath(".")

    print(f"Analizando el proyecto en: {project_path}")
    all_libraries = get_imported_libraries_from_project(project_path)
    third_party_libraries = filter_standard_libraries(all_libraries)

    print("\n🔍 Librerías detectadas en el proyecto:")
    for library in sorted(third_party_libraries):
        print(f"  - {library}")
    
    print("\n📦 Total de librerías detectadas:", len(third_party_libraries))

