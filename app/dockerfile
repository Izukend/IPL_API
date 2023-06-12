FROM python:bullseye

RUN pip install -v --no-cache-dir cython ipython mysql-connector-python  uwsgi PyJWT gunicorn
RUN pip install -v --no-build-isolation --no-binary :all: falcon
RUN pip install SQLAlchemy==1.4.4
COPY ipl_api/requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/ipl_api
CMD ["uwsgi", "uwsgi.ini"]
