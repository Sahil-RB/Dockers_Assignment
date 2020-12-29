FROM teamcloudyuga/python:alpine
COPY . /usr/src/app
WORKDIR /usr/src/app
ENV TEXT1 Hackfest 
ENV TEXT2 Registration 
ENV ORGANIZER UVCE 
RUN pip3 install -r requirements.txt
CMD python rsvp.py
