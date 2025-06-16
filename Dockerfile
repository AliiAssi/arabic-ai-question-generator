# Step 1: Use an official Python runtime as a parent image
# The README specifies Python 3.8+, so we'll use a recent, slim version.
FROM python:3.9-slim-buster

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the dependencies file first to leverage Docker's build cache.
# This way, dependencies are only re-installed if requirements.txt changes.
COPY requirements.txt ./

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code into the container.
# This includes the 'app/' directory, 'run.py', and any other project files.
COPY . .

# Step 6: Expose the port the app runs on.
# The README indicates the app is accessible on port 5000.
EXPOSE 5000

# Step 7: Define the command to run the application when the container starts.
# This executes the entry point script 'run.py'.
CMD ["python", "run.py"]