Deployment checklist

1. Prepare environment
   - Copy `.env.example` to `.env` and fill provider keys and `SECRET_KEY`.
   - Ensure `.env` is not committed to source control.

2. Build and run with Docker Compose (recommended for servers)

```bash
docker-compose up --build -d
```

3. Verify
   - API: `http://<HOST>:8000/health`
   - Docs: `http://<HOST>:8000/docs`

4. Mobile app
   - Run the Expo dev server in `mobile_app/` for testing.
   - For production, use Expo EAS to build native binaries, or publish via Expo.

5. Tips for production
   - Use a managed Postgres or other DB; set `DATABASE_URL` accordingly.
   - Run behind a reverse proxy (nginx) and enable HTTPS.
   - Use strong `SECRET_KEY` and rotate keys when needed.
