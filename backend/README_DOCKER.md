# Docker Files Information

## Why Are Docker Files Renamed?

The `Dockerfile` and `docker-compose.yml` have been renamed to `.backup` to prevent Render.com from automatically detecting and using Docker.

**Reason**: We want to use Render's **native Python environment** for faster, simpler deployments. Docker builds are slower and more complex for this use case.

## Files Renamed

- `Dockerfile` → `Dockerfile.backup`
- `docker-compose.yml` → `docker-compose.yml.backup`

## Using Docker Locally (Optional)

If you want to use Docker for local development, rename the files back:

```bash
# In the backend directory
mv Dockerfile.backup Dockerfile
mv docker-compose.yml.backup docker-compose.yml

# Run with Docker Compose
docker-compose up --build
```

## Using Docker on Render (Advanced)

If you specifically want to deploy with Docker on Render:

1. **Rename files back**:
   ```bash
   mv backend/Dockerfile.backup backend/Dockerfile
   ```

2. **Update `render.yaml`**:
   ```yaml
   services:
     - type: web
       name: filmosphere-backend
       env: docker
       dockerfilePath: ./backend/Dockerfile
       dockerContext: ./backend
   ```

3. **Fix Dockerfile context** - The Dockerfile needs adjustment:
   ```dockerfile
   # Make sure COPY paths match your backend directory structure
   COPY requirements.txt ./
   COPY . /app
   ```

4. **Commit and deploy**

## Recommendation

**For Render deployment**: Keep Docker files renamed (as `.backup`)
**For local development**: You can use either Docker or virtual environment

### Without Docker (Recommended for Local)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

### With Docker (If you prefer)

```bash
# Rename files first
mv backend/Dockerfile.backup backend/Dockerfile
mv backend/docker-compose.yml.backup backend/docker-compose.yml

# Then run
cd backend
docker-compose up
```

## Summary

- ✅ **Native Python builds** (current setup) - Faster, simpler, recommended for Render
- ⚙️ **Docker builds** (available as .backup) - More complex, slower, but consistent environment

The Docker files are preserved and can be restored anytime if needed.

