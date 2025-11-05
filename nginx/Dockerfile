# OpenMedia Nginx Dockerfile
FROM nginx:1.25-alpine

# Installer openssl pour générer des certificats auto-signés
RUN apk add --no-cache openssl

# Copier la configuration Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Créer les répertoires nécessaires
RUN mkdir -p /etc/nginx/ssl /var/cache/nginx /var/log/nginx

# Générer un certificat auto-signé par défaut (à remplacer en production)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Permissions
RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/ssl && \
    chmod 700 /etc/nginx/ssl && \
    chmod 600 /etc/nginx/ssl/*

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Exposer les ports
EXPOSE 80 443

# Démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]
