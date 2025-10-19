FROM mcr.microsoft.com/devcontainers/python:3.12

RUN sudo apt-get -y update \
                    && apt-get install -y xz-utils \
                    && apt-get install -y libgl1 \
                    && apt-get install -y poppler-utils \
                    && apt-get -y install tesseract-ocr

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
