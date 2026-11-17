# Weekly Status Report App

A locally hosted Flask application for recording ServiceNow incidents, RITMs, tasks, and other work, then preparing a weekly status report.

## Requirements

- Python 3.9+
- pip

## Setup

1. Put `app.py` and the `templates/index.html` file in the same project folder structure:

   ```text
   weekly-status/
   ├── app.py
   └── templates/
       └── index.html
   ```

2. Open a terminal in the `weekly-status` folder and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate it:

   **Windows PowerShell**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   source .venv/bin/activate
   ```

4. Install Flask:

   ```bash
   pip install Flask
   ```

5. Start the application:

   ```bash
   python app.py
   ```

6. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The app binds to `127.0.0.1`, so it is available only on the local computer by default. The `weekly_status.db` SQLite database is created beside `app.py` the first time the app starts.

## Using the app

- Choose a reporting week with the week selector and click **View Week**.
- Fill in **Add Work Item** to record an Incident, RITM, Task, or Other work. Date and title are required.
- Add a ServiceNow reference, description, status, priority, hours, and team as needed.
- Use **Delete** to remove an incorrect item.
- Complete the weekly outcomes and planning fields, then click **Save Weekly Report**.
- Use **Print / Save as PDF** to print the report or save it as a PDF from the browser.

## Data and privacy

All records are stored in the local `weekly_status.db` SQLite file. The application does not connect to ServiceNow or send data to a remote service. Avoid entering sensitive credentials or information that your organization's policies prohibit storing locally. Back up the database file if you need to preserve the records.
