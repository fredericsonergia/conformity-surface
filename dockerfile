# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt

RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y

# copy the content of the local src directory to the working directory
COPY src/ .

EXPOSE 8000:8000
# command to run on container start
CMD [ "python3", "./main.py" ]