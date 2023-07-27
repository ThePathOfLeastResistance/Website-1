FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /python-docker

# Copy the requirements.txt file to the working directory
COPY requirements.txt requirements.txt

# Install the dependencies specified in the requirements.txt file
RUN pip3 install -r requirements.txt

# Expose port 5000 for the application
EXPOSE 5000

# Copy the entire current directory to the working directory inside the container
COPY . .

# Start the Flask application container when starts
 theCMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]