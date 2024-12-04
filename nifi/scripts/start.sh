#!/bin/bash

# Espera de 1 minuto antes de comenzar la automatización
echo "Esperando 1 minuto antes de comenzar la automatización..."
sleep 60  # Espera de 60 segundos

# Intentar conectar a NiFi hasta que esté disponible
echo "Esperando a que NiFi esté disponible..."

# Intentar hasta que NiFi esté disponible (usando el nombre del contenedor 'nifi' y puerto 8443)
until curl -k -u admin:ctsBtRBKHRAx69EqUghvvgEvjnaLjFEB https://nifi:8443/nifi-api/system-diagnostics &>/dev/null; do
    echo "NiFi no está disponible, esperando 10 segundos para intentar de nuevo..."
    sleep 10
done

echo "NiFi está disponible. Subiendo el template..."

# Subir el template desde la carpeta de templates
curl -k -u admin:ctsBtRBKHRAx69EqUghvvgEvjnaLjFEB \
  -X POST \
  -F "template=@/opt/nifi/nifi-current/conf/templates/template.xml" \
  https://nifi:8443/nifi-api/process-groups/root/templates/upload

# Verificar que el template se ha subido correctamente
echo "Verificando templates cargados..."
curl -k -u admin:ctsBtRBKHRAx69EqUghvvgEvjnaLjFEB \
  https://nifi:8443/nifi-api/process-groups/root/templates