FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY reglas.py modelos.py patrones.py facade.py simulacion.py ./

CMD ["python", "-u", "simulacion.py"]
