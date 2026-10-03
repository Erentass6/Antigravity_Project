# Antigravity — Inventory Prototype

A small Flask and MongoDB inventory-management prototype. It includes account flows, product records, and a rule-based stock status estimate.

> **Status:** learning project. The stock analysis is a simple heuristic, not a trained AI model. Authentication and deployment settings are not production hardened.

## What it demonstrates

- Flask routes for login, registration, dashboard, and product records
- MongoDB persistence through PyMongo
- A basic stock-risk calculation based on current stock, daily sales, and lead time
- A small command-line entry point in `main.py`

## Stack

Python · Flask · PyMongo · MongoDB · Jinja templates

## Run locally

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`, then replace the sample `MONGO_URI` with a MongoDB connection string you control. Keep `.env` private; it is ignored by Git.
5. Start the web application:

   ```bash
   python app.py
   ```

6. Open <http://127.0.0.1:5001>.

The optional CLI entry point is `python main.py`. Both entry points need a valid MongoDB connection.

## Configuration

- `MONGO_URI` — MongoDB connection string
- `FLASK_DEBUG` — set to `1` only for local development; defaults off

Never commit live credentials. If a credential was previously committed, rotate it in the provider as well; deleting a file from the latest branch does not remove old Git history.

## License

No license has been specified yet.
