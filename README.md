# Chaat Corner

> A small, full-stack Indian street-food ordering app built with FastAPI and vanilla JavaScript.

Chaat Corner provides a customer-facing menu, cart and checkout flow, contact form, and a protected admin panel for managing menu items. The backend uses FastAPI and SQLAlchemy with SQLite for local development. The frontend is plain HTML, CSS, and JavaScript, so it needs no Node.js build step.

## Features

- Browse menu items and filter them by category.
- Add items to a cart, adjust quantities, and place an order.
- Submit customer contact messages.
- Authenticate an administrator with bcrypt and JWT.
- Create, update, hide, and delete menu items from the admin panel.
- Automatically create and seed the local database on first startup.
- Explore the API through FastAPI's interactive `/docs` page.

## Project structure

```text
app/
  main.py                 FastAPI application and CORS configuration
  config.py               Environment-backed settings
  database.py             SQLAlchemy engine, schema setup, and seed data
  auth.py                 Password and JWT helpers
  models/                 Database models
  schemas/                Pydantic request and response schemas
  routers/                API route handlers
frontend/
  index.html              Customer-facing page and admin panel
  styles.css              Responsive visual design
  app.js                  API client, cart, checkout, and admin behavior
src/gchy/                 Package entry point
```

## Requirements

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or another Python virtual environment
- A modern browser

## Configuration

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Then set the values in `.env`:

```dotenv
DATABASE_URL=sqlite:///./chaat.db
SECRET_KEY=replace-with-a-long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=the-generated-bcrypt-hash
FRONTEND_ORIGIN=http://localhost:3000
DEBUG=true
```

Generate a bcrypt password hash without putting the plain password in source control:

```powershell
uv run python -c "import bcrypt; print(bcrypt.hashpw(b'change-me', bcrypt.gensalt()).decode())"
```

Use the generated value for `ADMIN_PASSWORD_HASH`. Never commit `.env`, production secrets, or `chaat.db`.

## Run locally

Install dependencies and start the API:

```powershell
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Alternatively, use the included virtual environment:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

In a second terminal, serve the frontend:

```powershell
python -m http.server 3000 --directory frontend
```

Open <http://localhost:3000>. The API is available at <http://localhost:8000>, and interactive documentation is at <http://localhost:8000/docs>. The first API startup creates and seeds `chaat.db`.

To use another API URL from the browser, set this before refreshing:

```js
localStorage.setItem("gchy_api_url", "http://localhost:8000");
```

`FRONTEND_ORIGIN` must exactly match the frontend URL, including its port, because it controls CORS.

## API reference

### Public endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health message |
| `GET` | `/api/menu` | List menu items |
| `GET` | `/api/menu/{item_id}` | Get one menu item |
| `POST` | `/api/orders` | Create an order |
| `GET` | `/api/orders` | List orders |
| `GET` | `/api/orders/{order_id}` | Get one order |
| `PATCH` | `/api/orders/{order_id}/status` | Change order status |
| `POST` | `/api/contact` | Create a contact message |
| `GET` | `/api/contact` | List contact messages |

### Admin endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/admin/login` | Get a JWT bearer token |
| `POST` | `/api/menu` | Create a menu item |
| `PATCH` | `/api/menu/{item_id}` | Update a menu item |
| `DELETE` | `/api/menu/{item_id}` | Delete a menu item |

Login:

```json
{"username": "admin", "password": "your-password"}
```

Use the returned token for protected requests:

```http
Authorization: Bearer <token-from-/api/admin/login>
```

Create-order example:

```json
{
  "customer_name": "Asha",
  "customer_phone": "9876543210",
  "items": [{"menu_item_id": 1, "quantity": 2}]
}
```

Valid order statuses are `pending`, `confirmed`, `preparing`, `ready`, `completed`, and `cancelled`.

## Deployment notes

The backend and frontend can be deployed separately. For production:

- Use managed PostgreSQL rather than SQLite on ephemeral hosting.
- Add `psycopg[binary]` to `pyproject.toml` and run `uv lock` when using PostgreSQL.
- Set `DEBUG=false` and use a unique, long `SECRET_KEY`.
- Store `ADMIN_PASSWORD_HASH` as a bcrypt hash, never as a plain password.
- Set `FRONTEND_ORIGIN` to the exact HTTPS frontend origin.
- Configure persistent storage, HTTPS, and backups through the hosting provider.

## Validation

Check that the application imports successfully:

```powershell
uv run python -c "from app.main import app; print(app.title)"
```

With the API running, check the health endpoint:

```powershell
curl http://localhost:8000/
```

## Contributing

1. Create a branch for your change.
2. Keep secrets, databases, virtual environments, and generated files out of commits.
3. Run the validation commands and manually check the frontend before opening a pull request.
4. Explain configuration or API changes in the pull request description.

## License

No license has been selected for this project yet. Add a license before distributing or accepting external contributions.
