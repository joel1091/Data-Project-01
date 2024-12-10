| **Entidad**              | **Atributo**                         | **Tipo de dato**         | **Restricciones**    | **Descripción**                                    |
|---------------------------|--------------------------------------|--------------------------|----------------------|--------------------------------------------------|
| **centros_educativos**    | Geo Point                           | Geography                | Opcional             | Coordenadas geográficas del centro educativo.    |
|                           | Geo Shape                           | Geometry                 | Opcional             | Forma geográfica del centro educativo.           |
|                           | codcen                              | Integer                  | Único, no nulo       | Código único del centro educativo.               |
|                           | dlibre                              | Character varying (255)  | No nulo              | Nombre oficial del centro educativo.             |
|                           | dgenerica_                          | Character varying (255)  | Opcional             | Tipo genérico del centro educativo.              |
|                           | despecific                          | Character varying (255)  | Opcional             | Descripción específica del centro educativo.     |
|                           | regimen                             | Character varying (20)   | No nulo              | Régimen del centro educativo (público/concertado/privado). |
|                           | direccion                           | Character varying (255)  | No nulo              | Dirección completa del centro educativo.         |
|                           | codpos                              | Integer                  | No nulo              | Código postal del centro educativo.              |
|                           | municipio                           | Character varying (255)  | No nulo              | Municipio donde está ubicado el centro educativo.|
|                           | provincia                           | Character varying (255)  | No nulo              | Provincia donde está ubicado el centro educativo.|
|                           | telef                               | Integer                  | Opcional             | Número de teléfono del centro educativo.         |
|                           | fax                                 | Integer                  | Opcional             | Número de fax del centro educativo.              |
|                           | mail                                | Character varying (255)  | Opcional             | Dirección de correo electrónico del centro educativo. |
| **fgv_estaciones**        | gid                                 | Integer                  | Único, no nulo       | Identificador único de la estación.              |
|                           | Codi / Código                       | Integer                  | No nulo              | Código de la estación.                           |
|                           | Nom / Nombre                        | Character varying (255)  | No nulo              | Nombre oficial de la estación.                   |
|                           | Tipus / Tipo                        | Integer                  | Opcional             | Tipo de estación (categoría).                    |
|                           | Línea / Línea                       | Character varying (255)  | Opcional             | Líneas que pasan por la estación.                |
|                           | Próximas Arribades / Próximas Llegadas | Character varying (255)| Opcional           | URL con información de próximas llegadas.        |
|                           | geo_shape                           | Geometry                 | Opcional             | Forma geográfica de la estación.                 |
|                           | geo_point_2d                        | Geography                | Opcional             | Coordenadas geográficas en 2D de la estación.    |
| **hospitales**            | geo_point_2d                        | Geography                | Opcional             | Coordenadas geográficas del hospital.            |
|                           | geo_shape                           | Geometry                 | Opcional             | Forma geográfica del hospital.                   |
|                           | nombre                              | Character varying (255)  | No nulo              | Nombre del hospital.                             |
|                           | financiaci                          | Character varying (255)  | Opcional             | Tipo de financiación (pública/privada).          |
|                           | tipo                                | Character varying (255)  | Opcional             | Tipo de hospital (general/especializado).        |
|                           | camas                               | Integer                  | Opcional             | Número de camas disponibles en el hospital.      |
|                           | direccion                           | Character varying (255)  | Opcional             | Dirección completa del hospital.                 |
|                           | fecha                               | Date                     | Opcional             | Fecha de apertura del hospital.                  |
|                           | barrio                              | Character varying (255)  | Opcional             | Barrio donde está ubicado el hospital.           |
|                           | codbarrio                           | Integer                  | Opcional             | Código del barrio del hospital.                  |
| **idealista**             | objectid                            | Integer                  | Único, no nulo       | Identificador único del registro de precios.     |
|                           | geo_point_2d                        | Geography                | Opcional             | Coordenadas geográficas de la zona.              |
|                           | geo_shape                           | Geometry                 | Opcional             | Forma geográfica de la zona.                     |
|                           | barrio                              | Character varying (255)  | Opcional             | Nombre del barrio.                               |
|                           | distrito                            | Character varying (255)  | Opcional             | Nombre del distrito.                             |
|                           | precio_2022_euros_m2                | Numeric                  | Opcional             | Precio por metro cuadrado en 2022.               |
|                           | precio_2010_euros_m2                | Numeric                  | Opcional             | Precio por metro cuadrado en 2010.               |
|                           | max_historico_euros_m2              | Numeric                  | Opcional             | Precio máximo histórico por metro cuadrado.      |
| **ruido**                 | objectid                            | Integer                  | Único, no nulo       | Identificador único del registro de ruido.       |
|                           | gridcode                            | Integer                  | No nulo              | Código de la malla geográfica asociada al ruido. |
|                           | geo_shape                           | Geometry                 | Opcional             | Forma geográfica de la zona afectada por ruido.  |
|                           | geo_point_2d                        | Geography                | Opcional             | Coordenadas geográficas de la zona afectada.     |
| **vulnerabilidad_barrios**| objectid                            | Integer                  | Único, no nulo       | Identificador único del barrio.                  |
|                           | nombre                              | Character varying (255)  | No nulo              | Nombre del barrio.                               |
|                           | vul_equip_txt                       | Character varying (255)  | Opcional             | Vulnerabilidad por falta de equipamientos.       |
|                           | ind_dem                             | Numeric                  | Opcional             | Índice demográfico de vulnerabilidad.            |
|                           | ind_econom                         | Numeric                  | Opcional             | Índice económico de vulnerabilidad.              |
|                           | geo_shape                           | Geometry                 | Opcional             | Forma geográfica del barrio.                     |
| **discapacitados**     | objectid          | Integer                  | Único, no nulo       | Identificador único del equipamiento para discapacitados. |
|                        | equipamient       | Character varying (255)  | No nulo              | Nombre del equipamiento para discapacitados.     |
|                        | x                 | Integer                  | Opcional             | Coordenada X geográfica del equipamiento.        |
|                        | y                 | Integer                  | Opcional             | Coordenada Y geográfica del equipamiento.        |
|                        | identifca         | Integer                  | No nulo              | Código identificador del equipamiento.           |
|                        | codvia            | Integer                  | No nulo              | Código de la vía donde está ubicado el equipamiento. |
|                        | numportal         | Integer                  | Opcional             | Número del portal cercano al equipamiento.       |
|                        | telefono          | Integer                  | Opcional             | Número de teléfono del equipamiento.             |
|                        | geo_shape         | Geometry                 | Opcional             | Forma geográfica del equipamiento.               |
|                        | geo_point_2d      | Geography                | Opcional             | Coordenadas geográficas en 2D del equipamiento.  |
