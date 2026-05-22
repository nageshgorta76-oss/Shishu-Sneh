# Shishu-Sneh

Shishu-Sneh is a Streamlit-based baby care assistant for tracking early infant growth, vaccination reminders, feeding guidance, developmental milestones, and simple AI support in English, Hindi, and Kannada.

## Features

- Dashboard to save baby records with age, weight, and height.
- Input validation for baby name, age, weight, and height.
- BMI and saved-record summary metrics.
- Growth tracker with personal growth trends and reference charts.
- Vaccination schedule with due, due-soon, and upcoming guidance.
- Feeding and health awareness modules with local-friendly tips.
- Simple local assistant for common baby care questions.
- Admin mode for deleting baby records and managing the database.
- Export saved records as CSV.

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: create a `.env` file if you want to configure a custom database path:

```env
DATABASE_PATH=database.db
```

4. Run the app:

```bash
streamlit run app.py
```

5. Open the local Streamlit URL shown in the terminal.

## Admin Password

For Streamlit Cloud, add this secret:

```toml
admin_password = "change-this-password"
```

For local demos, the app falls back to `12345` if no Streamlit secret is configured.

## Notes

- The app stores data in `database.db` using SQLite.
- `database.db`, `.env`, Python cache files, and Streamlit secrets are ignored by Git.
- The assistant is rule-based and should not replace a pediatrician. Urgent or detailed medical concerns should be handled by a qualified doctor.
