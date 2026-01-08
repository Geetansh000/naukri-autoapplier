# Naukri Job Application Automation

An automated job application bot for Naukri.com that streamlines the job search and application process using AI-powered profile optimization.

## Features

- **Automated Job Applications**: Automatically apply to matching jobs on Naukri.com
- **AI-Powered Profile Optimization**: Uses Gemini/OpenAI to tailor profiles for job positions
- **Job Details Fetching**: Scrapes and analyzes job listings
- **Profile Management**: Automated bio and profile updates
- **Database Tracking**: Maintains records of applications and job history
- **CLI Interface**: Command-line tools for easy automation
- **Web Driver Support**: Supports both Selenium and browser automation

## Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Naukri.com account
- (Optional) Gemini or OpenAI API key for AI features

## Installation

1. Clone or download this repository:
```bash
cd naukri
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your settings in `app/config.py` or create a `.env` file with necessary credentials

## Configuration

Key configuration files:
- `app/config.py` - Main configuration settings
- `.gitignore` - Git ignore patterns
- `requirements.txt` - Python dependencies

Environment variables needed:
- `NAUKRI_USERNAME` - Your Naukri account username
- `NAUKRI_PASSWORD` - Your Naukri account password
- `GEMINI_API_KEY` or `OPENAI_API_KEY` - API keys for AI features (optional)

## Usage

### Command Line Interface
```bash
python -m app.cli [command] [options]
```

### Main Modules

- **`app/apply.py`** - Core job application logic
- **`app/auto_apply.py`** - Automated application workflows
- **`app/login.py`** - Naukri authentication
- **`app/getjobs.py`** - Fetch available job listings
- **`app/fetch_job_details.py`** - Extract detailed job information
- **`app/bio.py`** - Profile and biography management
- **`app/gemini.py`** - Gemini AI integration
- **`app/openai_helper.py`** - OpenAI integration
- **`app/db.py`** - Database operations
- **`app/helpers.py`** - Utility functions

## Project Structure

```
naukri/
├── app/
│   ├── answers.json      # Stored job responses
│   ├── answers.py        # Answer management
│   ├── apply.py          # Job application logic
│   ├── apply_web.py      # Web-based application
│   ├── auto_apply.py     # Automation workflow
│   ├── bio.py            # Profile management
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration
│   ├── db.py             # Database operations
│   ├── fetch_job_details.py  # Job scraping
│   ├── gemini.py         # Gemini AI helper
│   ├── getjobs.py        # Job listing fetching
│   ├── helpers.py        # Utility functions
│   ├── infer.py          # Inference logic
│   ├── initiate_apply.py # Application initialization
│   ├── login.py          # Authentication
│   ├── naukri_driver.py  # Browser automation
│   ├── openai_helper.py  # OpenAI integration
│   └── __pycache__/      # Python cache
├── answers.txt           # Job responses log
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Warning

⚠️ **Use Responsibly**: This tool automates job applications on Naukri.com. Ensure compliance with:
- Naukri.com's Terms of Service
- Your local laws and regulations
- Rate limiting and responsible bot usage

## License

Private project. Please respect intellectual property rights.

## Support

For issues or questions, review the code documentation and configuration files.
