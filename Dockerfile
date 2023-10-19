# Use the official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy your entire project into the container
COPY . .

# Copy the requirements file into the container and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install .

# Expose the port that your FastAPI app is running on (if not using reverse proxy)
EXPOSE 8000

# Command to run your FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
