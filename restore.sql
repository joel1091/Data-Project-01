
CREATE DATABASE data_project_01


--PRIMERA CARPETA->CULTURA Y OCIO

CREATE TABLE public.zones-dactivitats-zonas-de-actividades (
    Id. Falla integer NOT NULL,
    OBJECTID integer NOT NULL,
    geo_shape GEOMETRY(),
    geo_point_2d GEOGRAPHY()
)

CREATE TABLE public.centros-educativos-en-valencia (
    Geo Point GEOGRAPHY(),--------------
    Geo Shape GEOMETRY(),----------------
    codcen INTEGER  NOT NULL, --ESTO SERIA EL ID
    dlibre VARCHAR(255),        
    dgenerica_ VARCHAR(255),
    despecific VARCHAR(255),------------
    regimen VARCHAR(20),
    direccion VARCHAR(255),
    codpos INTEGER,
    municipio_ VARCHAR(255),
    provincia_ VARCHAR(255),
    telef INTEGER,
    fax INTEGER,
    mail VARCHAR(255)
)

CREATE TABLE public.monuments-turistics-monumentos-turisticos (
    gid INTEGER, --id monumento
    Nom/Nombre VARCHAR(255),-------------
    Portal INTEGER,
    Telèfon/Telefono INTEGER,
    Ruta INTEGER,
    Audio INTEGER,
    Escena VARCHAR(255),
    NomAudio/NombreAudio VARCHAR(255),
    geo_shape GEOMETRY(),---------------------
    geo_point_2d()-------------------
)

--SEGUNDA CARPETA->MEDIO AMBIENTE

CREATE TABLE public.recarrega-vehicles-electrics-recarga-vehiculos-electricos (
    objectid INTEGER, --ID
    PROYECTO VARCHAR(255),
    LOCALIZACIÓN VARCHAR(255), --nombre de la calle
    ESTADO VARCHAR(255),
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

CREATE TABLE public.espais-verds-espacios-verdes (
    objectid INTEGER, --ID
    Id Jardí / Id. Jardín INTEGER,
    Nom / Nombre VARCHAR(255),-------------
    Barri / Barrio VARCHAR(255),
    Tipologia / Tipología VARCHAR(255),
    Àrea / Área INTEGER,
    Número Elementos Fitness INTEGER,
    Superficie Huerto Urbano INTEGER,
    Zona VARCHAR(55),
    DM VARCHAR(255),
    Ud. Gestion VARCHAR(255),
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

--TERCERA CARPETA ->PRECIO VIVIENDA


CREATE TABLE public.precio-de-compra-en-fotocasa (
    Geo Point GEOMETRY(),----------------
    Geo Shape GEOGRAPHY(),------------------
    coddistbar INTEGER,
    codbarrio INTEGER,
    coddistrit INTEGER,
    DISTRITO VARCHAR(255),
    Precio_2022 (Euros/m2) INTEGER,
    Precio_2010 (Euros/m2) INTEGER,
    Max_historico (Euros/m2) INTEGER,
    Año_Max_Hist INTEGER,
    BARRIO VARCHAR(255),
    Fecha_creacion DATE
)

CREATE TABLE public.precio-de-compra-en-idealista (
    Geo Point GEOMETRY(),----------------
    Geo Shape GEOGRAPHY(),------------------
    coddistbar INTEGER,
    BARRIO VARCHAR(255),
    codbarrio INTEGER,
    coddistrit INTEGER,
    DISTRITO VARCHAR(255),
    Precio_2022 (Euros/m2) INTEGER,
    Precio_2010 (Euros/m2) INTEGER,
    Max_historico (Euros/m2) INTEGER,
    Año_Max_Hist INTEGER,
    Fecha_creacion DATE
)

--CUARTA CARPETA-> SALUD


CREATE TABLE public.hospitales (
    geo_point_2d GEOGRAPHY(),------------------
    geo_shape GEOMETRY(),----------------
    Nombre VARCHAR(255),
    Financiaci VARCHAR(255),
    Tipo VARCHAR(255),
    Camas INTEGER,
    Direccion VARCHAR(255),
    Fecha DATE,
    Barrio VARCHAR(255),
    codbarrio INTEGER,
    coddistbar INTEGER,
    coddistrit INTEGER,
    X INTEGER,
    Y INTEGER
)

CREATE TABLE public.mapa-soroll-24h-mapa-ruido-24h (
    Nivell / Nivel INTEGER,
    gid INTEGER,
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

--QUINTA CARPETA -> SOCIEDAD Y BIENESTAR

CREATE TABLE public.bancs-en-via-publica-bancos-en-via-publica (
    gid INTEGER,
    Modelo VARCHAR(255),
    Num. Banco INTEGER,
    Emplazamiento VARCHAR(255),
    Num. Policia INTEGER,
    Distrito VARCHAR(255),
    Barrio VARCHAR(255),
    Año Instalacion INTEGER,
    geo_point_2d GEOGRAPHY()------------------
) 

CREATE TABLE public.discapacitat-discapacidad (
    OBJECTID INTEGER,
    equipamien VARCHAR(255),
    x INTEGER,
    y INTEGER,
    identifica INTEGER,
    codvia INTEGER,
    numportal INTEGER,
    telefono INTEGER,
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)
CREATE TABLE public.majors-mayoresmajors-mayores (
    OBJECTID INTEGER,
    equipamien VARCHAR(255),
    x INTEGER,
    y INTEGER,
    identifica INTEGER,
    codvia INTEGER,
    numportal INTEGER,
    telefono INTEGER,
    gid INTEGER,
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)
CREATE TABLE public.migrants-migrantes (
    OBJECTID INTEGER,
    equipamien VARCHAR(255),
    x INTEGER,
    y INTEGER,
    identifica INTEGER,
    codvia INTEGER,
    numportal INTEGER,
    telefono INTEGER,
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)
CREATE TABLE public.vulnerabilidad-por-barrios (
    Geo Point GEOGRAPHY(),
    Geo Shape GEOMETRY(),
    Nombre VARCHAR(255),
    Codbar INTEGER,
    Distrito VARCHAR(255),
    Ind_Equip INTEGER,
    Vul_Equip VARCHAR(255),
    Ind_Dem INTEGER,
    Vul_Dem VARCHAR(255),
    Ind_Econom INTEGER,
    Vul_Econom VARCHAR(255),
    Ind_Global INTEGER,
    Vul_Global VARCHAR(255),
    Shape_Leng INTEGER,
    Shape_Area INTEGER
)

CREATE TABLE public.zones-jocs-infantils-zona-juegos-infantiles (
    objectid VARCHAR(255),
    Codigo INTEGER,
    Jardin VARCHAR(255),
    Barrio VARCHAR(255),
    DM INTEGER,
    Zona VARCHAR(255),
    Mantenimie VARCHAR(255),
    Tipo VARCHAR(255),
    CREATED_USER VARCHAR(255), ----------EN ESTOS 4 NO HAY DATOS
    CREATED_DATE VARCHAR(255),
    LAST_EDITED_USER VARCHAR(255),
    LAST_EDITED_DATE VARCHAR(255),
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

--SEXTA CARPETA ->TRANSPORTE

CREATE TABLE public.itinerarios-ciclistas-itineraris-ciclistes (
    Tipus / Tipo INTEGER,
    objectid INTEGER,
    st_length(shape) INTEGER,
    st_length(shape) INTEGER,
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)
CREATE TABLE public.emt (
    Id. Parada INTEGER,
    Cod. Via / Cod. Vía INTEGER,
    Num. Portal VARCHAR(255), ------------POSIBLE PROBLEMA (HAY NUM Y TEXTO)
    Suprimida INTEGER,
    Denominació / Denominación VARCHAR(255),
    Línies / Líneas VARCHAR(255), --------POSIBLE PROBLEMA ES UNA LISTA DE NUMS Y LETRAS
    Pròximes Arribades / Proximas Llegadas VARCHAR(255), ----ES UN LINK
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)
CREATE TABLE public.fgv-estacions-estaciones (
    gid INTEGER,
    Códi / Código INTEGER,
    Nom / Nombre VARCHAR(255),
    Tipus / Tipo INTEGER,
    Línia / Línea VARCHAR(255), -----PROBLEMA, ES UNA LISTA
    Pròximes Arribades / Próximas Llegadas VARCHAR(255), -- link
    proximes_llegadas VARCHAR(255),  --link
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

CREATE TABLE public.aparcaments-persones-mobilitat-reduida-aparcamientos-personas-movilidad-reducida (
    OBJECTID INTEGER,
    Nombre Places / Número Plazas INTEGER,
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

CREATE TABLE public.valenbisi-disponibilitat-valenbisi-dsiponibilidad (
    Direccion VARCHAR(255),
    Numero INTEGER,
    Activo VARCHAR(2), --Esto hay que convertirlo a TRUE FALSE (ES UN BOOL)
    Bicis_disponibles INTEGER,
    Espacios_libres INTEGER,
    Espacios_totales INTEGER,
    ticket VARCHAR(2), --Esto hay que convertirlo a TRUE FALSE (ES UN BOOL)
    fecha_actualizacion DATETIME, ---ESTO PUEDE DAR PROBLEMAS POR COMO LEE EL DATETIME (22/11/2024  12:16:47)
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY(),------------------
    update_jcd DATETIME ---ESTO PUEDE DAR PROBLEMAS POR COMO LEE EL DATETIME (22/11/2024  12:16:47)
)


CREATE TABLE public. (
    OBJECTID INTEGER,
    Carrer / Calle VARCHAR(255),
    Tipus Carrer / Tipo calle VARCHAR(25),
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)