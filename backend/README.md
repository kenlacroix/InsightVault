# InsightVault Backend Setup (Windows)

> **Windows users:**
> For the smoothest install, use `requirements-windows.txt`:
>
> ```sh
> pip install -r requirements-windows.txt
> ```
>
> This file contains only the versions and packages confirmed to work on Windows. For Linux/macOS, use `requirements.txt`.

## Prerequisites

- Python 3.8+
- Node.js (for frontend, optional)
- PostgreSQL (or SQLite for development)

## 1. Create and Activate a Virtual Environment (Recommended)

```sh
python -m venv venv
venv\Scripts\activate
```

## 2. Install Backend Dependencies (Windows)

**Step-by-step for Windows compatibility:**

1. **Install all dependencies at once (recommended):**

   ```sh
   pip install -r requirements-windows.txt
   ```

   > If you see errors about missing wheels or build tools, ensure you are using a recent version of pip and Python.

2. **If you see errors about missing Rust or build tools:**

   - Use the above versions, which are known to work without Rust on Windows.
   - Avoid installing advanced ML packages (like torch, transformers) unless you have a C++/Rust build environment.

3. **If you see errors about a missing package:**
   - Install it individually, e.g. `pip install <package>`

## 3. Environment Variables

- Copy `backend/.env.example` to `backend/.env` and fill in your secrets and database connection info.

## 4. Database Setup

- For development, you can use SQLite by setting `USE_SQLITE=true` in your `.env` file.
- For production, set up PostgreSQL and update `DATABASE_URL`.

## 5. Running the Backend

```sh
uvicorn app.main:app --reload
```

Or, if `uvicorn` is not in your PATH:

```sh
python -m uvicorn app.main:app --reload
```

## 6. Running Tests

```sh
pytest
```

---

**If you encounter issues, check:**

- Your Python version (`python --version`)
- That you are in the correct virtual environment
- That all dependencies are installed (see above)
- That your `.env` file is present and correct

For more help, see the main project README or open an issue.
