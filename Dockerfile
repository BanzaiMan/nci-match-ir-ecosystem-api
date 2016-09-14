# Base image 
FROM python:2.7.12

MAINTAINER jeremy.pumphrey@nih.gov

# Install requirements
RUN mkdir -p /nci-match-ir-ecosystem-api && chmod 777 /nci-match-ir-ecosystem-api
COPY requirements.txt /nci-match-ir-ecosystem-api/
RUN pip install -r /nci-match-ir-ecosystem-api/requirements.txt

# Add the app code 
COPY . /nci-match-ir-ecosystem-api/

# Default command 
#CMD ["python", "/nci-match-ir-ecosystem-api/app.py" ]
CMD cd /nci-match-ir-ecosystem-api && python ./app.py
