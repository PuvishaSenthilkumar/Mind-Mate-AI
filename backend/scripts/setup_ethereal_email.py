"""
Ethereal Email setup script for MindMate AI OTP testing.

Ethereal Email provides a fake SMTP service that captures emails for testing.
No real email credentials needed.

Note: The Ethereal Email API has changed. Please create an account manually:

1. Go to https://ethereal.email
2. Click "Create an Ethereal account" or use the web interface
3. Note down your SMTP credentials (username, password, SMTP host)
4. Update backend/.env with those credentials

Or use a real SMTP provider like Gmail with App Password.
"""
import sys
import os

def setup_ethereal():
    print("=" * 60)
    print("Ethereal Email Setup for MindMate AI OTP Testing")
    print("=" * 60)
    print("\n📧 Ethereal Email is a fake SMTP service for testing.")
    print("   It captures emails without actually sending them.\n")
    print("📝 Steps to set up:")
    print("   1. Go to https://ethereal.email")
    print("   2. Click 'Create an Ethereal account'")
    print("   3. Enter any name/email to create an account")
    print("   4. Copy the SMTP credentials shown")
    print("   5. Update backend/.env with those credentials")
    print("\n📋 Example .env configuration:")
    print("   SMTP_HOST=smtp.ethereal.email")
    print("   SMTP_PORT=587")
    print("   SMTP_USER=your-username@ethereal.email")
    print("   SMTP_PASSWORD=your-password")
    print("   SMTP_TLS=true")
    print("   EMAILS_FROM_EMAIL=your-username@ethereal.email")
    print("   EMAILS_FROM_NAME=MindMate AI")
    print("\n🔗 After setting up, view test emails at:")
    print("   https://ethereal.email/login")
    print("=" * 60)

if __name__ == "__main__":
    setup_ethereal()
