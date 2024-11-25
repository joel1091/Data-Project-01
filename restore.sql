
CREATE DATABASE data_project_01


--PRIMERA CARPETA->CULTURA Y OCIO

CREATE TABLE public.park (
    Id.Falla integer NOT NULL,
    OBJECTID integer NOT NULL,
    geo_shape GEOMETRY(),
    geo_point_2d GEOGRAPHY()
)

CREATE TABLE public.school (
    GeoPoint GEOGRAPHY(),--------------
    GeoShape GEOMETRY(),----------------
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

CREATE TABLE public.monument (
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

CREATE TABLE public.charging_point (
    objectid INTEGER, --ID
    PROYECTO VARCHAR(255),
    LOCALIZACIÓN VARCHAR(255), --nombre de la calle
    ESTADO VARCHAR(255),
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

CREATE TABLE public.green_zone (
    objectid INTEGER, --ID
    IdJardí/Id.Jardín INTEGER,
    Nom/Nombre VARCHAR(255),-------------
    Barri/Barrio VARCHAR(255),
    Tipologia/Tipología VARCHAR(255),
    Àrea/Área INTEGER,
    NúmeroLelementosFitness INTEGER,
    SuperficieHuertoUrbano INTEGER,
    Zona VARCHAR(55),
    DM VARCHAR(255),
    Ud.Gestion VARCHAR(255),
    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)

--TERCERA CARPETA ->PRECIO VIVIENDA


CREATE TABLE public. (

    geo_shape GEOMETRY(),----------------
    geo_point_2d GEOGRAPHY()------------------
)