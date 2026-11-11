FROM python:3.12-slim AS build
WORKDIR /app
COPY . .
RUN python -m pip install --no-cache-dir --upgrade pip && python -m pip install --no-cache-dir .

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
ENV PORT=5102
EXPOSE 5102
CMD ["sh", "-c", "uvicorn repuestos_del_taller.adapters.inbound.http.composicion:app --host 0.0.0.0 --port ${PORT}"]
