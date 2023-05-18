FROM python:3.10
WORKDIR /app
EXPOSE 80
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . . 
CMD ["python", "main.py"]
