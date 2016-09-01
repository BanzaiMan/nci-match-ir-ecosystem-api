# Base image 
FROM python:2.7.12

MAINTAINER jeremy.pumphrey@nih.gov

# Install requirements
RUN mkdir -p /nci-match-ir-ecoystem-api && chmod 777 /nci-match-ir-ecoystem-api
COPY requirements.txt /nci-match-ir-ecoystem-api/
RUN pip install -r /nci-match-ir-ecoystem-api/requirements.txt

# Add the app code 
COPY . /nci-match-ir-ecoystem-api/

# Default command 
CMD ["python", "/nci-match-ir-ecoystem-api/app.py" ]
