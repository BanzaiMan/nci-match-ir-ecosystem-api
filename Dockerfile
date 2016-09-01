# Base image 
FROM python:2.7

MAINTAINER jeremy.pumphrey@nih.gov

#ENV RAILS_VERSION 4.2.6
#ENV RAILS_ENV test
ENV HOME /nci-match-ir-ecoystem-api
WORKDIR $HOME 

# Add the app code 
ADD . $HOME 

RUN pip install -r ./requirements.txt

# Default command 
CMD ["python", "$HOME/app.py" ]
