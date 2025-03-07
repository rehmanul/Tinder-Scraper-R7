import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logger
logger = logging.getLogger(__name__)

class GoogleSheetsIntegration:
    """Google Sheets integration for Tinder Scraper application.
    
    This class handles all interactions with Google Sheets, including:
    - Reading and writing data to the spreadsheet
    - Logging extraction processes and errors
    - Creating and formatting sheets
    """
    
    def __init__(self, spreadsheet_id: str, credentials_file: str = 'credentials.json'):
        """Initialize the Google Sheets integration.
        
        Args:
            spreadsheet_id: The ID of the Google Sheets document
            credentials_file: Path to the service account credentials JSON file
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self.service = None
        self.sheets_initialized = False
        
        # Sheet names
        self.EXTRACTED_DATA_SHEET = 'Extracted Data'
        self.LOGS_SHEET = 'Extraction Process Logs'
        self.ERROR_LOGS_SHEET = 'Error Logs'
        
        # Initialize the service
        self._initialize_service()
    
    def _initialize_service(self) -> bool:
        """Initialize the Google Sheets API service.
        
        Returns:
            bool: True if service initialization was successful, False otherwise
        """
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes)
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {e}")
            return False
    
    def initialize_sheets(self) -> bool:
        """Initialize the spreadsheet by creating required sheets if they don't exist.
        
        Returns:
            bool: True if sheet initialization was successful, False otherwise
        """
        if not self.service:
            logger.error("Cannot initialize sheets: Google Sheets service not initialized")
            return False
        
        try:
            # Get existing sheets
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id).execute()
            existing_sheets = [sheet['properties']['title'] for sheet in sheet_metadata.get('sheets', [])]
            
            # Create required sheets if they don't exist
            requests = []
            
            # Extracted Data sheet
            if self.EXTRACTED_DATA_SHEET not in existing_sheets:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': self.EXTRACTED_DATA_SHEET
                        }
                    }
                })
            
            # Extraction Process Logs sheet
            if self.LOGS_SHEET not in existing_sheets:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': self.LOGS_SHEET
                        }
                    }
                })
            
            # Error Logs sheet
            if self.ERROR_LOGS_SHEET not in existing_sheets:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': self.ERROR_LOGS_SHEET
                        }
                    }
                })
            
            # Execute sheet creation requests
            if requests:
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': requests}
                ).execute()
                logger.info("Created missing sheets in the spreadsheet")
            
            # Initialize headers if sheets are empty
            self._initialize_sheet_headers()
            
            self.sheets_initialized = True
            logger.info("Sheets initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize sheets: {e}")
            return False
    
    def _initialize_sheet_headers(self) -> None:
        """Initialize headers for each sheet if they are empty."""
        try:
            # Extracted Data headers
            extracted_data_headers = [
                'Timestamp', 'Profile ID', 'Location', 'Image Count', 
                'Celibacy', 'Cooperativeness', 'Intelligence', 
                'Weight (kg)', 'Waist (cm)', 'Bust (cm)', 'Hips (cm)',
                'Gender', 'Age', 'Height (cm)', 'Face', 
                'Primary Ethnicity', 'Big Spender', 'Presentable',
                'Muscle %', 'Fat %', 'Dominance', 'Power', 'Confidence',
                'Full Labels JSON'
            ]
            self._ensure_headers(self.EXTRACTED_DATA_SHEET, extracted_data_headers)
            
            # Logs headers
            logs_headers = [
                'Timestamp', 'Profile ID', 'Location', 'Status', 'Details'
            ]
            self._ensure_headers(self.LOGS_SHEET, logs_headers)
            
            # Error Logs headers
            error_logs_headers = [
                'Timestamp', 'Error Type', 'Error Message', 'Location', 'Profile ID'
            ]
            self._ensure_headers(self.ERROR_LOGS_SHEET, error_logs_headers)
            
            logger.info("Sheet headers initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sheet headers: {e}")
    
    def _ensure_headers(self, sheet_name: str, headers: List[str]) -> None:
        """Ensure that a sheet has headers, adding them if it's empty.
        
        Args:
            sheet_name: Name of the sheet to check
            headers: List of header values to add if sheet is empty
        """
        try:
            # Check if the sheet has any data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1:Z1"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                # Sheet is empty, add headers
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1",
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
                
                # Format headers (make them bold)
                requests = [{
                    'repeatCell': {
                        'range': {
                            'sheetId': self._get_sheet_id(sheet_name),
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.95,
                                    'green': 0.95,
                                    'blue': 0.95
                                },
                                'textFormat': {
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }]
                
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': requests}
                ).execute()
                
                logger.info(f"Added headers to {sheet_name} sheet")
        except Exception as e:
            logger.error(f"Failed to ensure headers for {sheet_name}: {e}")
    
    def _get_sheet_id(self, sheet_name: str) -> Optional[int]:
        """Get the internal ID of a sheet by its name.
        
        Args:
            sheet_name: Name of the sheet to find
            
        Returns:
            Optional[int]: The sheet ID if found, None otherwise
        """
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id).execute()
            
            for sheet in sheet_metadata.get('sheets', []):
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            
            return None
        except Exception as e:
            logger.error(f"Failed to get sheet ID for {sheet_name}: {e}")
            return None
    
    def append_to_sheet(self, sheet_name: str, values: List[List[Any]]) -> bool:
        """Append rows to a sheet.
        
        Args:
            sheet_name: Name of the sheet to append to
            values: List of rows to append, where each row is a list of values
            
        Returns:
            bool: True if append was successful, False otherwise
        """
        if not self.service:
            logger.error("Cannot append to sheet: Google Sheets service not initialized")
            return False
        
        if not self.sheets_initialized:
            self.initialize_sheets()
        
        try:
            range_name = f"{sheet_name}!A:Z"
            body = {
                'values': values
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id, 
                range=range_name,
                valueInputOption='USER_ENTERED', 
                insertDataOption='INSERT_ROWS',
                body=body).execute()
            
            updated_rows = result.get('updates', {}).get('updatedRows', 0)
            logger.info(f"Appended {updated_rows} rows to {sheet_name}")
            return True
        except HttpError as error:
            logger.error(f"Google Sheets API error when appending to {sheet_name}: {error}")
            return False
        except Exception as e:
            logger.error(f"Failed to append to {sheet_name}: {e}")
            return False
    
    def get_sheet_data(self, sheet_name: str, range_notation: str = "A:Z") -> List[List[Any]]:
        """Get data from a sheet.
        
        Args:
            sheet_name: Name of the sheet to read from
            range_notation: A1 notation range to read (default: "A:Z")
            
        Returns:
            List[List[Any]]: List of rows, where each row is a list of values
        """
        if not self.service:
            logger.error("Cannot get sheet data: Google Sheets service not initialized")
            return []
        
        try:
            range_name = f"{sheet_name}!{range_notation}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            logger.info(f"Read {len(rows)} rows from {sheet_name}")
            return rows
        except Exception as e:
            logger.error(f"Failed to get data from {sheet_name}: {e}")
            return []
    
    def log_extraction(self, profile_id: str, location: str, status: str, details: str) -> bool:
        """Log an extraction process.
        
        Args:
            profile_id: ID of the profile being processed
            location: Location of the profile
            status: Status of the extraction (e.g., SCRAPED, SKIPPED, LOCATION_CHANGE)
            details: Additional details about the extraction
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[timestamp, profile_id, location, status, details]]
        return self.append_to_sheet(self.LOGS_SHEET, values)
    
    def log_error(self, error_type: str, error_message: str, location: str, profile_id: Optional[str] = None) -> bool:
        """Log an error.
        
        Args:
            error_type: Type of error (e.g., API Error, Network Error)
            error_message: Detailed error message
            location: Location being processed when the error occurred
            profile_id: ID of the profile being processed (if applicable)
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[timestamp, error_type, error_message, location, profile_id or 'N/A']]
        return self.append_to_sheet(self.ERROR_LOGS_SHEET, values)
    
    def save_profile_data(self, profile_data: Dict[str, Any]) -> bool:
        """Save profile data to the Extracted Data sheet.
        
        Args:
            profile_data: Dictionary containing profile data and labels
            
        Returns:
            bool: True if saving was successful, False otherwise
        """
        if not profile_data:
            logger.warning("Cannot save profile data: No data provided")
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            profile_id = profile_data.get('profile_id', 'Unknown')
            location = profile_data.get('location', 'Unknown')
            image_count = len(profile_data.get('images', []))
            
            # Extract labels
            labels = profile_data.get('labels', {})
            
            # Handle gender specially (it's a more complex structure)
            gender_labels = labels.get('gender', [])
            gender_str = "Unknown"
            if gender_labels:
                # Find the gender with the highest maximum value
                max_gender = max(gender_labels, key=lambda x: x.get('value', [0, 0])[1])
                gender_str = max_gender.get('name', 'Unknown')
            
            # Find primary ethnicity
            ethnicity_labels = labels.get('ethnicity', [])
            primary_ethnicity = "Unknown"
            if ethnicity_labels:
                # Find the ethnicity with the highest maximum value
                max_ethnicity = max(ethnicity_labels, key=lambda x: x.get('value', [0, 0])[1])
                primary_ethnicity = max_ethnicity.get('name', 'Unknown')
            
            # Format range values for display
            def format_range(range_values):
                if not range_values or len(range_values) < 2:
                    return "N/A"
                return f"{range_values[0]} - {range_values[1]}"
            
            # Create row data
            row_data = [
                timestamp,
                profile_id,
                location,
                image_count,
                format_range(labels.get('celibacy', [])),
                format_range(labels.get('cooperativeness', [])),
                format_range(labels.get('intelligence', [])),
                format_range(labels.get('weight', [])),
                format_range(labels.get('waist', [])),
                format_range(labels.get('bust', [])),
                format_range(labels.get('hips', [])),
                gender_str,
                format_range(labels.get('age', [])),
                format_range(labels.get('height', [])),
                format_range(labels.get('face', [])),
                primary_ethnicity,
                format_range(labels.get('big_spender', [])),
                format_range(labels.get('presentable', [])),
                format_range(labels.get('muscle_percentage', [])),
                format_range(labels.get('fat_percentage', [])),
                format_range(labels.get('dominance', [])),
                format_range(labels.get('power', [])),
                format_range(labels.get('confidence', [])),
                json.dumps(labels)  # Full labels as JSON
            ]
            
            return self.append_to_sheet(self.EXTRACTED_DATA_SHEET, [row_data])
        except Exception as e:
            logger.error(f"Failed to save profile data: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from the Extracted Data sheet.
        
        Returns:
            Dict[str, Any]: Dictionary containing statistics
        """
        if not self.service:
            logger.error("Cannot get statistics: Google Sheets service not initialized")
            return {}
        
        try:
            # Get all data from Extracted Data sheet
            data = self.get_sheet_data(self.EXTRACTED_DATA_SHEET)
            
            if not data or len(data) <= 1:  # Only header or no data
                return {
                    'totalProfiles': 0,
                    'totalImages': 0,
                    'locations': {},
                    'ageDistribution': {},
                    'ethnicityDistribution': {}
                }
            
            # Skip header row
            data = data[1:]
            
            # Extract basic statistics
            total_profiles = len(data)
            total_images = sum(int(row[3]) if len(row) > 3 and row[3].isdigit() else 0 for row in data)
            
            # Location distribution
            locations = {}
            for row in data:
                if len(row) > 2:
                    location = row[2]
                    locations[location] = locations.get(location, 0) + 1
            
            # Age distribution
            age_distribution = {}
            for row in data:
                if len(row) > 12:
                    age_range = row[12]
                    if "-" in age_range:
                        try:
                            min_age, max_age = map(int, age_range.split("-"))
                            avg_age = (min_age + max_age) // 2
                            decade = (avg_age // 5) * 5  # Group by 5-year intervals
                            age_group = f"{decade}-{decade+4}"
                            age_distribution[age_group] = age_distribution.get(age_group, 0) + 1
                        except ValueError:
                            pass
            
            # Ethnicity distribution
            ethnicity_distribution = {}
            for row in data:
                if len(row) > 15:
                    ethnicity = row[15]
                    ethnicity_distribution[ethnicity] = ethnicity_distribution.get(ethnicity, 0) + 1
            
            # Return compiled statistics
            return {
                'totalProfiles': total_profiles,
                'totalImages': total_images,
                'locations': locations,
                'ageDistribution': age_distribution,
                'ethnicityDistribution': ethnicity_distribution
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def clear_sheet_data(self, sheet_name: str, preserve_header: bool = True) -> bool:
        """Clear data from a sheet.
        
        Args:
            sheet_name: Name of the sheet to clear
            preserve_header: Whether to preserve the header row (default: True)
            
        Returns:
            bool: True if clearing was successful, False otherwise
        """
        if not self.service:
            logger.error("Cannot clear sheet: Google Sheets service not initialized")
            return False
        
        try:
            # Determine range to clear
            range_to_clear = f"{sheet_name}!A2:Z" if preserve_header else f"{sheet_name}!A1:Z"
            
            # Clear the range
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_to_clear,
                body={}
            ).execute()
            
            logger.info(f"Cleared data from {sheet_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear data from {sheet_name}: {e}")
            return False
    
    def get_recent_logs(self, log_type: str = 'extraction', limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent logs from the specified log sheet.
        
        Args:
            log_type: Type of log to retrieve ('extraction' or 'error')
            limit: Maximum number of logs to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of log entries
        """
        sheet_name = self.LOGS_SHEET if log_type == 'extraction' else self.ERROR_LOGS_SHEET
        
        try:
            # Get data from sheet
            data = self.get_sheet_data(sheet_name)
            
            if not data or len(data) <= 1:  # Only header or no data
                return []
            
            # Extract header and data rows
            headers = data[0]
            rows = data[1:]
            
            # Sort by timestamp (descending)
            rows.sort(key=lambda x: x[0] if x else "", reverse=True)
            
            # Limit the number of rows
            rows = rows[:limit]
            
            # Convert to dictionaries
            logs = []
            for row in rows:
                log_entry = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        log_entry[header] = row[i]
                    else:
                        log_entry[header] = ""
                logs.append(log_entry)
            
            return logs
        except Exception as e:
            logger.error(f"Failed to get recent logs from {sheet_name}: {e}")
            return []
