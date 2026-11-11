FROM node:22-alpine AS build
WORKDIR /app
COPY . .
RUN for d in mfe-*; do (cd $d && npm install --no-audit --no-fund && npm run build) || exit 1; done
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/mfe-shell/dist /usr/share/nginx/html
COPY --from=build /app/mfe-intervenciones/dist /usr/share/nginx/html/mfe/mfe-intervenciones
COPY --from=build /app/mfe-repuestos-del-taller/dist /usr/share/nginx/html/mfe/mfe-repuestos-del-taller
