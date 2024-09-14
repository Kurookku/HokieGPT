# Use the official Python 3.8 image as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

# Install Next.js dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the Next.js app will run
EXPOSE 3000

# Start the Next.js app
CMD ["npm", "run", "dev"]