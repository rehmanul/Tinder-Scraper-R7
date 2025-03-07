from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import logging
import threading
import time
from datetime import datetime
from werkzeug.utils import secure_filename

# Import custom modules
from tinder_scraper import TinderScraper
from google_sheets_integration import GoogleSheetsIntegration
from config import Config
from utils.image_processor import ImageProcessor
from utils.label_generator import LabelGenerator
from location_manager import LocationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tinder_scraper_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure output directory exists
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, 
            static_folder=Config.STATIC_DIR, 
            template_folder=Config.TEMPLATES_DIR)

# Initialize services
sheets_integration = GoogleSheetsIntegration(
    spreadsheet_id=Config.GOOGLE_SHEETS_ID,
    credentials_file=Config.CREDENTIALS_FILE
)

# Initialize utility classes
image_processor = ImageProcessor(output_dir=Config.OUTPUT_DIR)
label_generator = LabelGenerator()
location_manager = LocationManager(locations=Config.LOCATIONS)

# Global state for scraping status
scraping_status = {
    'is_active': False,
    'profiles_scraped': 0,
    'current_location': None,
    'start_time': None,
    'end_time': None,
    'target_profiles': 0,
    'errors': []
}

# Background scraping thread function
def scrape_profiles_thread(email, password, target_profiles, locations):
    global scraping_status
    
    try:
        # Update status
        scraping_status['is_active'] = True
        scraping_status['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scraping_status['profiles_scraped'] = 0
        scraping_status['target_profiles'] = target_profiles
        scraping_status['errors'] = []
        
        # Initialize scraper
        scraper = TinderScraper(
            email=email,
            password=password,
            output_dir=Config.OUTPUT_DIR,
            headless=True,
            google_sheets_integration=sheets_integration
        )
        
        # Run scraping session
        profiles_scraped = scraper.run_scraping_session(
            target_profiles=target_profiles,
            locations=locations
        )
        
        # Update status
        scraping_status['profiles_scraped'] = profiles_scraped
        scraping_status['is_active'] = False
        scraping_status['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"Scraping completed. Scraped {profiles_scraped}/{target_profiles} profiles")
    
    except Exception as e:
        # Update status with error
        scraping_status['is_active'] = False
        scraping_status['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scraping_status['errors'].append(str(e))
        
        logger.error(f"Error in scraping thread: {e}")


# Routes
@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')

@app.route('/data-center')
def data_center():
    """Render the data center page."""
    return render_template('data_center.html')

@app.route('/logs')
def logs():
    """Render the logs page."""
    return render_template('logs.html')

@app.route('/stryke-center')
def stryke_center():
    """Render the statistics and reports page."""
    return render_template('stryke_center.html')

@app.route('/labeling')
def labeling():
    """Render the labeling tool page."""
    return render_template('labeling.html')

@app.route('/api/start-scraping', methods=['POST'])
def start_scraping():
    """API endpoint to start a scraping session."""
    if scraping_status['is_active']:
        return jsonify({"status": "error", "message": "A scraping session is already running"})
    
    try:
        data = request.json
        target_profiles = data.get('target_profiles', 100)
        locations = data.get('locations', location_manager.get_locations())
        
        # Start a background thread for scraping
        thread = threading.Thread(
            target=scrape_profiles_thread,
            args=(Config.TINDER_EMAIL, Config.TINDER_PASSWORD, target_profiles, locations)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success", 
            "message": f"Started scraping session for {target_profiles} profiles"
        })
    
    except Exception as e:
        logger.error(f"Error starting scraping: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/scraping-status')
def get_scraping_status():
    """API endpoint to get the current scraping status."""
    return jsonify(scraping_status)

@app.route('/api/get-stats')
def get_stats():
    """API endpoint to get scraping statistics."""
    try:
        # Get stats from Google Sheets
        stats = sheets_integration.get_statistics()
        
        # If still scraping, add real-time profile count
        if scraping_status['is_active']:
            stats['totalProfiles'] = scraping_status['profiles_scraped']
        
        # Format stats for the UI
        formatted_stats = {
            "totalProfiles": stats.get('totalProfiles', 0),
            "currentMilestone": min(5, stats.get('totalProfiles', 0) // Config.PROFILES_PER_MILESTONE + 1),
            "profilesInCurrentMilestone": stats.get('totalProfiles', 0) % Config.PROFILES_PER_MILESTONE,
            "currentLocation": scraping_status.get('current_location', "Not scraping"),
            "profilesAtCurrentLocation": 0  # This would need to be tracked separately
        }
        
        return jsonify(formatted_stats)
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            "totalProfiles": 0,
            "currentMilestone": 1,
            "profilesInCurrentMilestone": 0,
            "currentLocation": "Error",
            "profilesAtCurrentLocation": 0
        })

@app.route('/api/get-recent-profiles')
def get_recent_profiles():
    """API endpoint to get recently scraped profiles."""
    try:
        # In a real implementation, this would query a database
        # For this demo, we'll return mock data
        
        # Generate mock profiles
        profiles = []
        for i in range(10):
            profile_id = f"{i+1:05d}"
            profiles.append({
                "profile_id": profile_id,
                "location": "New York, USA" if i % 2 == 0 else "London, UK",
                "image_count": 5 + (i % 3),
                "scraped_at": (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            })
        
        return jsonify({"profiles": profiles})
    
    except Exception as e:
        logger.error(f"Error getting recent profiles: {e}")
        return jsonify({"profiles": []})

@app.route('/api/get-logs', methods=['GET'])
def get_logs():
    """API endpoint to get logs from Google Sheets."""
    try:
        log_type = request.args.get('type', 'extraction')
        limit = int(request.args.get('limit', 50))
        
        logs = sheets_integration.get_recent_logs(log_type, limit)
        return jsonify({"logs": logs})
    
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({"logs": [], "error": str(e)})

@app.route('/api/images/<path:filename>')
def get_image(filename):
    """API endpoint to serve scraped images."""
    return send_from_directory(Config.OUTPUT_DIR, filename)

@app.route('/api/save-labels', methods=['POST'])
def save_labels():
    """API endpoint to save profile labels."""
    try:
        data = request.json
        profile_id = data.get('profile_id')
        labels = data.get('labels')
        
        # In a real implementation, this would save to a database
        # For this demo, we'll just log the data
        logger.info(f"Saving labels for profile {profile_id}")
        
        # Store the updated labels
        if sheets_integration:
            sheets_integration.update_profile_labels(profile_id, labels)
        
        return jsonify({"status": "success", "message": "Labels saved successfully"})
    
    except Exception as e:
        logger.error(f"Error saving labels: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/export-labels', methods=['GET'])
def export_labels():
    """API endpoint to export labels as JSON."""
    try:
        # In a real implementation, this would query a database
        # For this demo, we'll generate mock data
        
        export_data = {
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "profiles": []
        }
        
        # Generate mock labeled profiles
        for i in range(10):
            profile_id = f"{i+1:05d}"
            export_data["profiles"].append({
                "profile_id": profile_id,
                "location": "New York, USA" if i % 2 == 0 else "London, UK",
                "labels": {
                    "age": [25, 30],
                    "height": [165, 175],
                    "weight": [55, 65],
                    "intelligence": [75, 90],
                    "cooperativeness": [60, 85],
                    "confidence": [70, 90],
                    # Add other labels as needed
                }
            })
        
        # Create response with attachment headers
        response = jsonify(export_data)
        response.headers["Content-Disposition"] = "attachment; filename=tinder_labels_export.json"
        return response
    
    except Exception as e:
        logger.error(f"Error exporting labels: {e}")
        return jsonify({"status": "error", "message": str(e)})

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize Google Sheets
    try:
        sheets_integration.initialize_sheets()
        logger.info("Google Sheets initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets: {e}")
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=debug)
