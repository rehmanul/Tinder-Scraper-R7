# Tinder Profile Scraper and Labeling Platform

A comprehensive solution for scraping Tinder profiles, downloading images, and labeling them according to specific criteria.

## Overview

This application provides an end-to-end solution for collecting and labeling Tinder profile data for research purposes. The system includes:

- Automated profile scraping from Tinder
- Image downloading and storage
- Profile data organization
- Manual labeling interface for categorizing images
- Statistics and reporting
- Google Sheets integration for data storage and logging

## Features

- **Profile Scraper**: Automated tool to scrape profiles from Tinder using Selenium
- **Location Rotation**: Automatically rotates through different locations to collect diverse profiles
- **Image Download**: Downloads and organizes profile images
- **Data Center**: View and explore collected profiles and images
- **Labeling Tool**: Intuitive interface for labeling profiles according to the specified criteria
- **Logs Viewer**: Monitor scraping activities and track errors
- **Statistics Dashboard**: Visualize collection progress and data distribution
- **Google Sheets Integration**: Store data, logs, and labeled profiles in Google Sheets

## Installation

### Prerequisites

- Python 3.9+
- Google Chrome or Chromium
- ChromeDriver compatible with your Chrome version
- Google Cloud Platform account with Sheets API enabled
- Tinder Premium account

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tinder-scraper.git
   cd tinder-scraper
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Google Sheets API:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Sheets API
   - Create service account credentials
   - Download the credentials JSON file and save it as `credentials.json` in the project root

5. Configure environment variables:
   - Copy `config.env.example` to `.env`
   - Fill in your Tinder credentials, Google Sheets ID, and other configuration options

## Usage

### Running the Application

Start the Flask web server:

```bash
python app.py
```

Access the web interface at `http://localhost:5000`

### Dashboard

The dashboard provides an overview of the scraping progress and system status. From here, you can:

- Start new scraping sessions
- View current progress
- Access other parts of the application

### Data Center

The Data Center allows you to browse through the collected profiles. Features include:

- Filtering profiles by location, ethnicity, etc.
- Viewing profile images and details
- Previewing profile labels

### Labeling Tool

The Labeling Tool provides an interface for adding detailed labels to scraped profiles according to the specified criteria:

- Categorize profiles by various attributes
- Set value ranges for each attribute
- Save and export labeled data

### Logs

The Logs section displays detailed logs of scraping sessions and errors:

- Extraction process logs
- Error logs
- Filtering and searching capabilities

### Statistics

The Statistics dashboard visualizes the data collection progress and distributions:

- Progress towards milestones
- Distribution of profiles by location
- Age and ethnicity distributions
- Label value distributions

## Scraping Process

The scraping process follows these steps:

1. Authenticate with Tinder
2. Change location to a target city
3. Scrape profiles, collecting details and images
4. Filter out profiles with fewer than 5 usable images
5. Download and store images
6. Log the process in Google Sheets
7. Rotate to a new location after collecting 20 profiles

## Project Structure

```
tinder_scraper_project/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── config.env.example         # Environment variables template
├── credentials.json           # Google API credentials
├── static/                    # Static assets
├── templates/                 # HTML templates
├── tinder_images/             # Directory to store scraped images
├── tinder_scraper.py          # Tinder scraper module
├── google_sheets_integration.py  # Google Sheets integration module
└── utils/                     # Utility functions
```

## Labeling Criteria

The labeling follows these specific criteria:

- **Celibacy**: 0-100
- **Cooperativeness**: 0-100
- **Intelligence**: 0-100
- **Weight**: Range in kg
- **Waist**: Range in cm
- **Bust**: Range in cm
- **Hips**: Range in cm
- **Gender**: Male/Female percentages
- **Age**: Range in years
- **Height**: Range in cm
- **Face**: 0-100
- **Ethnicity**: Percentages across different ethnicities
- **Big Spender**: 0-100
- **Presentable**: 0-100
- **Muscle Percentage**: 0-100
- **Fat Percentage**: 0-100
- **Dominance**: 0-100
- **Power**: 0-100
- **Confidence**: 0-100

## Data Storage

- **Images**: Stored locally in the `tinder_images` directory
- **Profile Data**: Stored in Google Sheets
- **Labels**: Stored in Google Sheets
- **Logs**: Stored in Google Sheets and local log files

## Ethical Considerations

This tool is designed for research purposes only. When using it, please adhere to these guidelines:

- Do not share raw images that can identify individuals
- Respect Tinder's terms of service
- Use the data only for the stated research purposes
- Ensure proper data anonymization
- Do not use the tool for commercial purposes without proper authorization

## Troubleshooting

### Common Issues

- **Selenium Issues**: If you encounter issues with Selenium, ensure you have the correct ChromeDriver version installed
- **Google Sheets API**: Verify that your credentials have the correct permissions
- **Rate Limiting**: If you're being rate-limited by Tinder, try decreasing the scraping speed or using a different account

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Selenium for browser automation
- Flask for the web interface
- Google for Sheets API
