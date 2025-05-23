import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import pandas as pd
from config import Config
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsIntegration:
    def __init__(self):
        self.credentials_file = Config.GOOGLE_SHEETS_CREDENTIALS
        self.sheet_id = Config.GOOGLE_SHEETS_ID
        self.client = None
        self.worksheet = None
        self.setup_client()
    
    def setup_client(self):
        """Setup Google Sheets client"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            
            self.client = gspread.authorize(credentials)
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up Google Sheets client: {e}")
            raise
    
    def get_knowledge_base_data(self, worksheet_name: str = "knowledge_base") -> List[Dict[str, Any]]:
        """Fetch knowledge base data from Google Sheets"""
        try:
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet(worksheet_name)
            
            # Get all records
            records = worksheet.get_all_records()
            
            logger.info(f"Fetched {len(records)} records from Google Sheets")
            return records
            
        except Exception as e:
            logger.error(f"Error fetching data from Google Sheets: {e}")
            return []
    
    def log_conversation(self, conversation_data: Dict[str, Any], worksheet_name: str = "conversations"):
        """Log conversation data to Google Sheets"""
        try:
            sheet = self.client.open_by_key(self.sheet_id)
            
            try:
                worksheet = sheet.worksheet(worksheet_name)
            except:
                # Create worksheet if it doesn't exist
                worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
                # Add headers
                headers = ['session_id', 'user_id', 'message', 'response', 'timestamp', 'confidence']
                worksheet.append_row(headers)
            
            # Prepare row data
            row_data = [
                conversation_data.get('session_id', ''),
                conversation_data.get('user_id', ''),
                conversation_data.get('user_message', ''),
                conversation_data.get('bot_response', ''),
                conversation_data.get('timestamp', ''),
                conversation_data.get('confidence', '')
            ]
            
            worksheet.append_row(row_data)
            logger.info("Conversation logged to Google Sheets")
            
        except Exception as e:
            logger.error(f"Error logging conversation to Google Sheets: {e}")
    
    def update_knowledge_base(self, data: List[Dict[str, Any]], worksheet_name: str = "knowledge_base"):
        """Update knowledge base in Google Sheets"""
        try:
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet(worksheet_name)
            
            # Clear existing data
            worksheet.clear()
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(data)
            
            # Add headers
            headers = df.columns.tolist()
            worksheet.append_row(headers)
            
            # Add data rows
            for _, row in df.iterrows():
                worksheet.append_row(row.tolist())
            
            logger.info(f"Updated {len(data)} records in Google Sheets")
            
        except Exception as e:
            logger.error(f"Error updating knowledge base in Google Sheets: {e}")
            raise