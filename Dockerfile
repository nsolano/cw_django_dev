# Usa la imagen oficial de Python
FROM python:3.8

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de la aplicación al contenedor
COPY . .

# Ejecuta las migraciones
RUN python manage.py migrate

# Ejecuta el script create_users.py
RUN python manage.py shell < scripts/create_users.py

# Expone el puerto 8000 para que Django pueda ser accedido
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
