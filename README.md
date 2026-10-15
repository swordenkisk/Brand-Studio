# Brand Studio

An Arabic-first brand identity and packaging concept studio powered by OpenRouter.

## Requirements

- Python 3.10+
- An OpenRouter API key
- An image-capable model available to your OpenRouter account for image generation

## Run locally

```bash
chmod +x run.sh
./run.sh
On the first run, add OPENROUTER_API_KEY to .env, then run ./run.sh again.

Brand identity studio: http://localhost:8000
Image studio: http://localhost:8000/image-studio
Health check: http://localhost:8000/api/health
Run with Docker
bash


cp .env.example .env
Set OPENROUTER_API_KEY in .env, then run:

bash


docker compose up --build
API endpoints
GET /api/health
GET /api/models
GET /api/image-models
POST /api/design
POST /api/images
Image generation request
json


{
  "prompt": "A premium coffee package concept, dark green paper box, botanical details, studio product photography, no readable text",
  "model": "provider/image-model",
  "aspect\_ratio": "1:1",
  "resolution": "1K"
}
Image-model identifiers are loaded dynamically from OpenRouter. Model-specific supported parameters can vary; check the model capabilities before using optional parameters.

