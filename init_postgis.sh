#!/bin/bash
# Esperar a que el servicio de PostgreSQL esté disponible
until pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Esperando a que PostgreSQL esté listo..."
  sleep 2
done

# Instalar PostGIS (Para poder utilizar el GEOJSON dentro del postgres)
echo "Instalando PostGIS..."
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"
echo "PostGIS instalado correctamente."
