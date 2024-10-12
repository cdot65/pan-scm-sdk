# Installation Guide for pan-scm-sdk

This guide will help you install the `pan-scm-sdk` tool in your Python environment.

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.10 or higher**: Ensure Python is installed on your system.
- **pip**: Python package installer should be available.
- **Access to SCM Tenants**: You need valid credentials for both source and destination SCM tenants.

## Installation Steps

### 1. Create a Virtual Environment (Optional but *HIGHLY* Recommended)

It's good practice to use a virtual environment to manage dependencies.

**On macOS and Linux:**

<div class="termy">

<!-- termynal -->

```bash
$ python3 -m venv scm-env
$ source scm-env/bin/activate
```

</div>

**On Windows:**

<div class="termy">

<!-- termynal -->

```bash
$ python3 -m venv scm-env
$ scm-env\Scripts\activate
```

</div>

### 2. Install `pan-scm-sdk` via pip

Within the activated environment, install the package using pip:

<div class="termy">

<!-- termynal -->

```bash
$ pip install pan-scm-sdk
---> 100%
Successfully pan-scm-sdk
```

</div>

---

Now you're ready to use `pan-scm-sdk`. Proceed to the [Getting Started](getting-started.md) guide to begin cloning
configurations.
