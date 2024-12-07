import streamlit as st
import pydeck as pdk
from colegios import load_data as load_colegios_data, assign_colors
from cajeros import load_atm_data
from centros_mayores import load_centros_mayores_data
from discapacidad import load_discapacidad_data  # Importación de la función para discapacidad

# Función para generar la leyenda de colores de las capas
def color_legend(capas_seleccionadas):
    legend_html = ""
    colores = {
        "Colegios": "blue",          # Azul para colegios
        "Cajeros": "pink",           # Rosa para cajeros
        "Centros de Mayores": "black", # Negro para centros de mayores
        "Discapacidad": "purple"     # Morado para discapacidad
    }
    for capa in capas_seleccionadas:
        if capa in colores:
            legend_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="height: 12px; width: 12px; background-color: {colores[capa]}; border-radius: 50%; margin-right: 8px;"></div>
                <span>{capa}</span>
            </div>
            """
    return legend_html

# Aplicación principal
def main():
    st.title("Mapa Interactivo: Colegios, Cajeros, Centros de Mayores y Discapacidad")

    # Panel izquierdo: Configuración general
    st.sidebar.title("Opciones Generales")
    capas = st.sidebar.multiselect(
        "Selecciona las capas que deseas ver:",
        options=["Colegios", "Cajeros", "Centros de Mayores", "Discapacidad"],  # Incluye todas las capas
        default=["Colegios", "Cajeros", "Centros de Mayores", "Discapacidad"]
    )

    # Panel derecho: Configuración para colegios
    st.sidebar.title("Opciones para Colegios")
    tiene_hijos = st.sidebar.radio(
        "¿Tiene hijos en edad de ir al colegio?",
        ("No", "Sí")
    )

    regimen_opcion = None
    if tiene_hijos == "Sí":
        regimen_opcion = st.sidebar.selectbox(
            "¿A qué tipo de colegio le gustaría llevar a su hijo?",
            ("Todos los tipos", "CONCERTADO", "PÚBLICO", "PRIVADO")
        )

    # Cargar los datos de las capas seleccionadas
    colegios_data = load_colegios_data() if "Colegios" in capas and tiene_hijos == "Sí" else None
    cajeros_data = load_atm_data() if "Cajeros" in capas else None
    centros_mayores_data = load_centros_mayores_data() if "Centros de Mayores" in capas else None
    discapacidad_data = load_discapacidad_data() if "Discapacidad" in capas else None

    # Filtrar los colegios si la opción "Sí" fue seleccionada
    if colegios_data is not None:
        if regimen_opcion != "Todos los tipos":  # Filtrar solo si no se selecciona "Todos los tipos"
            colegios_data = colegios_data[colegios_data["regimen"] == regimen_opcion]
        colegios_data = assign_colors(colegios_data)

    # Configurar el estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=39.4699,  # Coordenadas aproximadas de Valencia
        longitude=-0.3763,
        zoom=13,
        pitch=0  # Sin inclinación (2D)
    )

    layers = []

    # Crear capa de colegios
    if colegios_data is not None and not colegios_data.empty:
        colegios_layer = pdk.Layer(
            "ScatterplotLayer",
            data=colegios_data,
            get_position=["lon", "lat"],
            get_color="color",  # Usar la columna de colores asignados
            radius_min_pixels=5,  # Tamaño constante de los puntos
            pickable=True
        )
        layers.append(colegios_layer)

    # Crear capa de cajeros
    if cajeros_data is not None and not cajeros_data.empty:
        cajeros_layer = pdk.Layer(
            "ScatterplotLayer",
            data=cajeros_data,
            get_position=["lon", "lat"],
            get_color=[255, 105, 180, 160],  # Rosa con transparencia
            get_radius=20,  # Tamaño de los puntos
            pickable=True
        )
        layers.append(cajeros_layer)

    # Crear capa de centros de mayores
    if centros_mayores_data is not None and not centros_mayores_data.empty:
        centros_mayores_layer = pdk.Layer(
            "ScatterplotLayer",
            data=centros_mayores_data,
            get_position=["lon", "lat"],
            get_color=[96, 96, 96, 255],  # Gris oscuro con opacidad máxima
            radius_min_pixels=8,  # Tamaño constante de los puntos
            pickable=True
        )
        layers.append(centros_mayores_layer)

    # Crear capa de discapacidad
    if discapacidad_data is not None and not discapacidad_data.empty:
        discapacidad_layer = pdk.Layer(
            "ScatterplotLayer",
            data=discapacidad_data,
            get_position=["lon", "lat"],
            get_color=[128, 0, 128, 255],  # Morado
            radius_min_pixels=8,  # Tamaño constante de los puntos
            pickable=True
        )
        layers.append(discapacidad_layer)

    # Configurar el tooltip dinámico
    tooltip = {
        "html": """
        <b>Nombre:</b> {nombre}<br>
        <b>Dirección:</b> {direccion}<br>
        <b>Teléfono:</b> {telefono}
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }

    # Crear y mostrar el mapa con las capas seleccionadas
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11",
        tooltip=tooltip
    )

    st.pydeck_chart(r)

    # Mostrar la leyenda a la derecha
    st.markdown("<h3>Capas Seleccionadas</h3>", unsafe_allow_html=True)
    legend = color_legend(capas)
    st.markdown(legend, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
