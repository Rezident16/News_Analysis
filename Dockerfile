# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define environment variable
ENV PORT=5000

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]


# docker run -p 5000:5000 -e API_KEY=PKX1AV0JF2GMVDO2XF2F -e API_SECRET=pjVDLxIoACRmP3WynjRnXoGfNeDS59KVa1RwNaiq -e BASE_URL=https://paper-api.alpaca.markets news-image
# flask run --host=0.0.0.0 --port=5000
