FROM python:3.12 as base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY VotingSystem/ .

EXPOSE 8000

FROM base as development

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=VotingSystem.settings.development"]

FROM base as production

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=VotingSystem.settings.production"]