FROM python:3.11-slim-b

WORKDIR /python-docker

# Copy the requirements.txt file to the working directory
COPY requirements.txt /python-docker/requirements.txt

# Install the dependencies specified in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the application
EXPOSE 5000

# Copy the entire current directory to the working directory inside the container
COPY . /python-docker

# Start the Flask application container when starts

# Fixed the typo in the CMD command by changing 'theCMD' to 'CMD'
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]