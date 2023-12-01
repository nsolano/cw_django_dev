# Etapa 1: Construcción
FROM python:3.8-alpine AS builder

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN apk --update add --no-cache gcc musl-dev libffi-dev
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de la aplicación al contenedor
COPY . .


# Etapa 2: Producción
FROM python:3.8-alpine

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.8 /usr/local/lib/python3.8

COPY . .

# Establece las variables del entorno virtual
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Ejecuta las migraciones
RUN python manage.py migrate

# Ejecuta el script create_users.py
RUN python manage.py shell < scripts/create_users.py

# Expone el puerto 8000 para que Django pueda ser accedido
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
