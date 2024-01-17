# Use an official Python runtime as a parent image
FROM python:3.8-slim

RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /Users/linerva/Desktop/pyapp

# Copy the current directory contents into the container at /usr/src/app
COPY . /Users/linerva/Desktop/pyapp

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

ENV NAME mine
# Run app.py when the container launches
CMD ["python", "./pyapp/views.py"]

