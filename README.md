# Stock Movement Analysis

### macOS and Linux

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Windows Command Prompt

Create a virtual environment:

```bat
python -m venv .venv
```

Activate it:

```bat
.venv\Scripts\activate.bat
```

## Install Packages

With the virtual environment activated, run:

```bash
pip install -r requirements.txt
```

## Run the application

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --reload
```

Open the application at:

```text
http://127.0.0.1:8000
```
