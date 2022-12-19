FROM python:3
WORKDIR /app
COPY requirements.txt /app
RUN python3 -m pip install -r requirements.txt

COPY . /app
EXPOSE 8080

CMD ["python", "app.py"]
