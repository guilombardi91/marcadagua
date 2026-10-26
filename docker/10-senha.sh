#!/bin/sh
# Gera o arquivo de senha do nginx a partir das variáveis AUTH_USER e AUTH_PASSWORD.
# Sem as duas variáveis o container não sobe, para o sistema nunca ficar aberto sem senha.
set -e
if [ -z "$AUTH_USER" ] || [ -z "$AUTH_PASSWORD" ]; then
    echo "ERRO: defina AUTH_USER e AUTH_PASSWORD nas variáveis de ambiente." >&2
    exit 1
fi
printf '%s:%s\n' "$AUTH_USER" "$(printf '%s' "$AUTH_PASSWORD" | openssl passwd -apr1 -stdin)" > /etc/nginx/.htpasswd
chmod 640 /etc/nginx/.htpasswd
chown root:nginx /etc/nginx/.htpasswd
