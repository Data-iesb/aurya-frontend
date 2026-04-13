FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --cache-dir=/cache -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]