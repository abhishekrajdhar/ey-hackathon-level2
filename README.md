# Agentic RFP Backend

The **Agentic RFP Backend** is a powerful system designed to automate the end-to-end process of handling Request for Proposals (RFPs). It leverages AI agents to scan for opportunities, match technical specifications, calculate pricing, and generate comprehensive proposals.

## Features

- **Sales Agent**: Automatically scans target portals for new RFPs, analyzing eligibility and deadlines.
- **Technical Matching**: Parses complex RFP documents (PDFs) and matches line items against an internal product inventory.
- **Pricing Engine**: Calculates total costs including materials, tests, and overheads.
- **Proposal Generation**: Drafts complete proposal documents ready for review.
- **Inventory Management**: API to manage products and pricing.
- **AI-Powered**: Uses Google Gemini for intelligent document parsing and decision making.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.10+
- **Database**: PostgreSQL (with SQLAlchemy)
- **AI/LLM**: Google Gemini
- **Web Scraping**: Selenium, BeautifulSoup
- **PDF Processing**: pdfplumber, pytesseract

## Prerequisites

- Python 3.10 or higher
- PostgreSQL installed and running
- Google Cloud API Key (for Gemini)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/abhishekrajdhar/ey-hackathon-level2
    cd ey-hackathon-level2
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root directory.
2.  Add the following environment variables:

    ```env
    # Database Connection
    DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/rfp_db

    # Google Gemini API Key
    GEMINI_API_KEY=your_gemini_api_key_here

    # Application Settings
    PROJECT_NAME="Agentic RFP Backend"
    ENVIRONMENT=dev
    ```

## Database Setup

Initialize the database tables using the provided script:

```bash
python -m app.create_db
```

## Usage

1.  **Start the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Access the API Documentation:**
    - Open your browser and navigate to `http://localhost:8000/docs` to see the interactive Swagger UI.
    - Check `http://localhost:8000/redoc` for alternative documentation.

## Key Endpoints

-   **Sales Scan**: `GET /api/v1/sales/scan` - Check for new RFPs.
-   **Run Pipeline**: `GET /api/v1/pipeline/run` - Execute the full agentic workflow.
-   **Inventory**: `POST /api/v1/inventory/products` - Add new products.
-   **Health**: `GET /health` - System status.

## Testing

Run the test suite using pytest:

```bash
pytest
```
