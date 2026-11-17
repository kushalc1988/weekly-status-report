# Weekly Status Report

This project is a locally hosted Flask application that helps you track ServiceNow work (Incidents, RITMs, Tasks, and other work) for a specific week and generate a weekly status report.

## Features

- Add work items by date and category
- Record ServiceNow references and detailed notes
- Categorize items by status, priority, and team
- Log hours spent
- Review weekly trends with simple graphical summaries
- Capture:
  - achievements
  - blockers / reasons something was not completed
  - actions needed to address gaps
  - risks and dependencies
  - pending follow-ups with other teams
  - production deployment planning
- Print or save the report as PDF from the browser

## Tech stack

- Python 3.9+
- Flask
- SQLite

## Local setup

1. Clone the repository
2. Open a terminal in the project folder
3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate it:

   Windows PowerShell:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Run the application:

   ```bash
   python app.py
   ```

7. Open the app in your browser:

   ```text
   http://127.0.0.1:5000
   ```

## Files

- `app.py` — Flask app and database logic
- `templates/index.html` — UI for entering data and viewing reports
- `instructions.md` — local setup instructions
- `requirements.txt` — Python dependencies

## Notes

- The app stores data in a local SQLite file named `weekly_status.db`.
- All data remains local to your machine unless you deliberately back it up or move it.
