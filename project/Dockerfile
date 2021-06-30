FROM python:2.7
LABEL maintainer="Firman Rosdiansyah"

COPY techtrends /techtrends
WORKDIR /techtrends
RUN pip install -r requirements.txt

RUN python ./init_db.py

EXPOSE 3111

# command to run on container start
CMD [ "python", "app.py" ]