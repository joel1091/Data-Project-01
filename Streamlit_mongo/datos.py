import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")  # Cambia 'localhost' si estás en otro entorno
db = client["data_DataProject"]  # Nombre de tu base de datos

# Obtener todas las colecciones
collections = db.list_collection_names()

# Función para obtener datos de una colección seleccionada
def get_data(collection_name):
    collection = db[collection_name]
    data = list(collection.find())
    if data:
        df = pd.DataFrame(data)
        return df
    else:
        return pd.DataFrame()

# Selección de la colección
st.sidebar.header("Selecciona una categoría")
selected_collection = st.sidebar.selectbox("Colección", collections)

if selected_collection:
    # Obtener los datos de la colección seleccionada
    df = get_data(selected_collection)

    # Mostrar los datos en formato tabular
    if not df.empty:
        st.subheader(f"Datos de la colección: {selected_collection}")
        st.dataframe(df)  # Mostrar los datos de forma tabular
    else:
        st.error(f"No se encontraron datos en la colección '{selected_collection}'.")
else:
    st.error("Por favor selecciona una colección en el menú lateral.")
