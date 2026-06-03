FROM python:3.10-slim

# Set up a working directory
WORKDIR /code

# Copy requirements and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of your application code
COPY . .

# Expose port 7860 (Hugging Face requires the app to listen on port 7860)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
