FROM python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
EXPOSE 8000
WORKDIR /home
COPY Pipfile Pipfile.lock /home/
RUN pip install pipenv && pipenv install --system
COPY . /home/
CMD ["gunicorn","-k","uvicorn.workers.UvicornH11Worker","--log-level","warning","main:app","-b","0.0.0.0:8000"]