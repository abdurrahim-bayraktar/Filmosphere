## Filmosphere API

This service provides search and rich aggregated details for films based on IMDb IDs.

### Search Films

- **Endpoint**: `GET /api/search?q=<query>`

Example:

```bash
curl "http://localhost:8000/api/search?q=Inception"
```

### Film Details

- **Endpoint**: `GET /api/films/{imdb_id}`

Example:

```bash
curl "http://localhost:8000/api/films/tt1375666"
```

### Film Trailer

- **Endpoint**: `GET /api/films/{imdb_id}/trailer`

### Film Streaming Sources

- **Endpoint**: `GET /api/films/{imdb_id}/streaming`

The full OpenAPI description is generated via drf-spectacular and saved to `docs/openapi.yaml`.


