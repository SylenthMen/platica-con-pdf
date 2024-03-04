# Usar una imagen base oficial de Python
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos primero para aprovechar la caché de capas
COPY requirements.txt .

# Instalar dependencias de Python
# RUN python -m venv --copies /opt/venv \
#     && . /opt/venv/bin/activate \
#     && pip install --upgrade pip \
#&& pip install -r requirements.txt
RUN python -m venv --copies /opt/venv
RUN . /opt/venv/bin/activate
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Establecer variables de entorno
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el resto del código de la aplicación al directorio de trabajo
COPY . .

# Comando para ejecutar la aplicación
#CMD ["gunicorn", "app:app", "-w", "4", "--threads", "2", "-b", "0.0.0.0:8000"]
CMD gunicorn app:app --workers 1 --threads 2 -b :$PORT

