# Site estático da marca d'água: nginx servindo web/index.html na porta 80, protegido por login e senha
FROM nginx:1.27-alpine
RUN apk add --no-cache openssl
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/10-senha.sh /docker-entrypoint.d/10-senha.sh
RUN sed -i 's/\r$//' /docker-entrypoint.d/10-senha.sh && chmod +x /docker-entrypoint.d/10-senha.sh
COPY web/ /usr/share/nginx/html/
EXPOSE 80
