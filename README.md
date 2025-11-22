# ChillBot Backend (Railway)

Mental health chatbot ML backend deployed on Railway.

## Local Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend.py
```

## Environment Variables

Set in Railway dashboard:
- `FLASK_ENV=production`
- `ALLOWED_ORIGINS=https://your-app.vercel.app`

## API Endpoints

- `GET /` - Service info
- `GET /api/health` - Health check
- `POST /api/analyze` - Analyze message
- `POST /api/mood/log` - Log mood
- `GET /api/mood/trend` - Get trend
- `GET /api/resources` - Get resources

## Deployment

Push to GitHub → Railway auto-deploys