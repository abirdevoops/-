# 🛡️ TruthLens AI — Bangladesh Digital Authenticity Demo

TruthLens AI is a bilingual (বাংলা + English) Streamlit application that screens images for signals associated with AI-generated/deepfake content.

## Included features

- Individual user registration
- Secure password hashing with PBKDF2 + unique salt
- Login / logout
- Separate user scan history
- Admin dashboard
- User and scan statistics
- SQLite persistent database
- AI-generated image screening
- Conservative 3-way result: Likely AI / Likely Real / Human Review
- EXIF/metadata inspection
- Explainable result
- Premium dark/cyan UI
- বাংলা + English interface
- CPU/GPU auto selection
- Streamlit Cloud ready

## Project structure

```text
truthlens_ai/
├── app.py
├── auth.py
├── detector.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── .gitignore
└── .streamlit/
    └── config.toml
```

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Admin setup

The database is SQLite (`truthlens.db`) and is created automatically.

For a demo admin account, set an environment variable before starting:

Windows CMD:

```cmd
set TRUTHLENS_ADMIN_EMAIL=your-email@example.com
streamlit run app.py
```

PowerShell:

```powershell
$env:TRUTHLENS_ADMIN_EMAIL="your-email@example.com"
streamlit run app.py
```

Then register using that email. On startup the account is promoted to admin.

For Streamlit Cloud, add `TRUTHLENS_ADMIN_EMAIL` to the app environment/secrets if you want admin bootstrap.

## Streamlit Cloud

1. Create a GitHub repository.
2. Upload the project files.
3. Open Streamlit Community Cloud.
4. Deploy the repository.
5. Main file: `app.py`.
6. Add the admin environment variable if required.

### Persistence warning

SQLite works well for a prototype/demo. However, Streamlit Cloud environments can be ephemeral. For a production deployment where account history must survive redeployments, replace SQLite with a persistent hosted database such as PostgreSQL/Supabase.

## AI detector

The prototype uses:

`rahulshendre/deepfake-detector-model-v1`

The model is downloaded at runtime; model weights should not be committed to GitHub.

## Important limitation

AI-image detection is probabilistic. No detector should be treated as absolute proof. New generators, editing, screenshots, compression and distribution shifts can cause errors.

TruthLens therefore uses a human-review zone and tells users to verify the original source, date and context.

## Competition roadmap

Next version can add:

- Multiple independent detectors / ensemble
- Frequency-domain forensic analysis
- Image URL analysis
- Video frame analysis
- Provenance / source verification
- Bengali explanation generation
- Privacy-preserving temporary image processing
- Calibration using a Bangladesh-focused evaluation dataset
- PDF evidence report
- Admin moderation and analytics
- Persistent PostgreSQL/Supabase database
