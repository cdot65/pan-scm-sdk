# trunk-ignore-all(terrascan/AC_DOCKER_0047)
# Use an official Python runtime as a parent image, based on Alpine
FROM python:3.12-alpine

# Install dependencies required for compiling certain Python packages
# gcc and musl-dev are required for compiling C extensions
# libffi-dev is required for the cffi package
# make is often required for building packages
RUN apk add --no-cache gcc musl-dev libffi-dev make

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified
RUN pip install --no-cache-dir pan-scm-sdk==0.1.0

# Set the locale to avoid issues with emoji rendering
ENV LANG=C.UTF-8

# Create a non-root user
RUN adduser -D panadmin
USER panadmin
