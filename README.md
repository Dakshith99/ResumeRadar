# ResumeRadar

## Overview
ResumeRadar is a project designed to extract, analyze, and present information from resumes. It consists of several components that work together to achieve this goal.

## Features

⭐ 1. **Info:**
   - Contains scripts and templates for extracting information from resumes.
   - Includes an `app.py` file for running the extraction process.
   - Has a `requirements.txt` file listing the necessary dependencies.

⭐ 2. **Dashboard:**
   - Hosts a web interface for interacting with the extracted data.
   - Contains a main `app.py` file for serving the dashboard.
   - Includes static files and templates for the web interface.
   - Has a `requirements.txt` file for dashboard-specific dependencies.

⭐ 3. **Model:**
   - Contains scripts and data for processing and analyzing resume data.
   - Includes a `main.py` file for running the model.
   - Stores resume data in `resume_data.csv`.

⭐ 4. **Automated Parsing:**
   - Utilizes machine learning models to automatically parse and extract relevant information from resumes.
   - Supports various resume formats for seamless integration.

⭐ 5. **Data Visualization:**
   - Provides visual insights into the extracted data using interactive charts and graphs on the dashboard.
   - Allows users to filter and sort data for better analysis.

⭐ 6. **User Management:**
   - Includes authentication and user management features to secure access to the dashboard.
   - Supports role-based access control for different user types.

⭐ 7. **Integration Support:**
   - Offers APIs for integrating with external systems to enhance functionality.
   - Facilitates data export in various formats for external use.

## How to Run

1. **Install Dependencies:**
   - Navigate to each component directory (Info-extractor, Dashboard, Model) and run `pip install -r requirements.txt` to install the necessary dependencies.

2. **Run the Info-extractor:**
   - Navigate to the `Info-extractor` directory.
   - Run `python app.py` to start the information extraction process.

3. **Run the Dashboard:**
   - Navigate to the `dashboard` directory.
   - Run `python app.py` to start the web interface.
   - Access the dashboard via `http://localhost:5000` in your web browser.

4. **Run the Model:**
   - Navigate to the `model` directory.
   - Run `python main.py` to process and analyze resume data.

## Technical Stack
- Python is used for scripting and running the main applications.
- Flask (or a similar framework) is likely used for the web dashboard.
- Dependencies are managed via `requirements.txt` files in each component.
