# trunk-ignore-all(terrascan/AC_DOCKER_0047)
# Use an official Python runtime as a parent image, based on Alpine
FROM python:3.12-alpine

# Add build argument for version
ARG SDK_VERSION

# Install dependencies required for compiling certain Python packages
# gcc and musl-dev are required for compiling C extensions
# libffi-dev is required for the cffi package
# make is often required for building packages
RUN apk add --no-cache gcc musl-dev libffi-dev make

# Set the working directory in the container to /app
WORKDIR /app

# Copy the distribution files
COPY dist/ /app/dist/

# Install the package from local dist directory using the version specified by build arg
RUN if [ -z "$SDK_VERSION" ] ; then \
        echo "Error: SDK_VERSION build argument is required" && exit 1 ; \
    else \
        pip install --no-cache-dir /app/dist/pan_scm_sdk-${SDK_VERSION}-py3-none-any.whl ; \
    fi

# Set the locale to avoid issues with emoji rendering
ENV LANG=C.UTF-8

# Create a non-root user
RUN adduser -D panadmin
USER panadmin
