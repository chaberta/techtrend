FROM python:2.7
LABEL maintainer="Audric Chabert"

COPY . /techtrends
WORKDIR /techtrends
RUN pip install -r requirements.txt
EXPOSE 6111
# command to run on container start
CMD [ "python", "app.py" ]