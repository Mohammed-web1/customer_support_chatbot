#!/usr/bin/env python3
'''
Setup script for AI Customer Support Chatbot
Run this script to initialize the system
'''

import os
import sys
import json
import sqlite3
from pathlib import Path

def create_directories():
    '''Create necessary directories'''
    directories = [
        'data',
        'chroma_db',
        'logs',
        'uploads'
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")

def create_env_file():
    '''Create .env file template'''
    env_template = '''# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Database Configuration
DATABASE_URL=sqlite:///./chatbot.db

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_ID=your_google_sheet_id_here

# Webhook Configuration
WEBHOOK_SECRET=your_webhook_secret_here
WEBHOOK_URL=https://your-domain.com/webhook

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Embedding Model Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
'''
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✓ Created .env file template")
        print("⚠️  Please update .env file with your actual API keys and configuration")
    else:
        print("✓ .env file already exists")

def create_sample_credentials():
    '''Create sample Google Sheets credentials file'''
    if not os.path.exists('credentials.json'):
        sample_creds = {
            "type": "service_account",
            "project_id": "your-project-id",
            "private_key_id": "your-private-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
            "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
            "client_id": "your-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
        }
        
        with open('credentials.json', 'w') as f:
            json.dump(sample_creds, f, indent=2)
        print("✓ Created sample credentials.json")
        print("⚠️  Please replace credentials.json with your actual Google Service Account credentials")
    else:
        print("✓ credentials.json already exists")

def create_sample_knowledge_base():
    '''Create sample knowledge base data'''
    sample_kb = [
        {
            "id": "1",
            "title": "Account Login Issues",
            "content": "If you're having trouble logging into your account, try resetting your password using the 'Forgot Password' link on the login page. Make sure you're using the correct email address associated with your account.",
            "category": "Account",
            "tags": "login, password, account, reset"
        },
        {
            "id": "2",
            "title": "Billing Questions",
            "content": "For billing inquiries, you can view your current plan and payment history in your account settings. If you need to update your payment method or have questions about charges, please contact our billing department.",
            "category": "Billing",
            "tags": "billing, payment, charges, subscription"
        },
        {
            "id": "3",
            "title": "Product Features",
            "content": "Our platform offers advanced analytics, real-time reporting, and team collaboration tools. You can access these features from your dashboard after logging in.",
            "category": "Features",
            "tags": "features, analytics, reporting, collaboration"
        }
    ]
    
    kb_file = Path('data/sample_knowledge_base.json')
    if not kb_file.exists():
        with open(kb_file, 'w') as f:
            json.dump(sample_kb, f, indent=2)
        print("✓ Created sample knowledge base")
    else:
        print("✓ Sample knowledge base already exists")

def initialize_database():
    '''Initialize SQLite database'''
    try:
        from database.models import create_tables
        create_tables()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Error creating database tables: {e}")
        print("You may need to run this after installing dependencies")

def main():
    '''Main setup function'''
    print("🚀 Setting up AI Customer Support Chatbot...\n")
    
    try:
        create_directories()
        create_env_file()
        create_sample_credentials()
        create_sample_knowledge_base()
        initialize_database()
        
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update .env file with your API keys")
        print("2. Replace credentials.json with your Google Service Account credentials")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Run the application: python main.py")
        print("5. Access the API documentation at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()