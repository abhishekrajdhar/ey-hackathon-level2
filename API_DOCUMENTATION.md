# API Documentation

Base URL: `https://example.com/api/v1`

## 1. Sales Agent
### Scan for RFPs
**Endpoint**: `GET /sales/scan`
**Description**: Scans provided URLs for eligible RFPs due within the specified timeframe.

**Parameters**:
- `urls` (query, list[str]): List of RFP portal URLs to scan.
  - Default: `["https://example-lstk1.com/tenders", "https://example-lstk2.com/rfps"]`
- `months` (query, int): Lookahead window in months. Default: `3`.

**Response**: `List[RFPSummary]`
```json
[
  {
    "id": "RFP-002",
    "title": "Annual Cable Supply - West Zone",
    "source_url": "https://power-grid-west.com/procurement",
    "due_date": "2025-12-31",
    "days_to_due": 30,
    "short_scope_summary": "3.5C 185sqmm Al XLPE..."
  }
]
```

## 2. Main Pipeline
### Run Full Response Generation
**Endpoint**: `GET /pipeline/run`
**Description**: Triggers the full agentic workflow (Sales -> Technical -> Pricing -> Proposal) for the best RFP found.

**Parameters**:
- `urls` (query, list[str]): List of URLs to scan.
- `live_mode` (query, bool): Set `true` to scrape live sites, `false` to use DB mock data. Default: `false`.

**Response**: `FullRFPResponse`
```json
{
  "rfp_summary": { ... },
  "technical_table": [
    {
      "line_id": 1,
      "description": "3.5C 185sqmm Al XLPE...",
      "quantity_m": 12000.0,
      "selected_sku": {
        "sku": "AP-CABLE-003",
        "name": "AP Aluminum XLPE...",
        "spec_match_percent": 100.0
      }
    }
  ],
  "pricing_table": {
    "total_material_cost": 5040000.0,
    "total_tests_cost": 40000.0,
    "grand_total": 5080000.0,
    "rows": [ ... ]
  }
}
```

## 3. Inventory Management
### Create Product
**Endpoint**: `POST /inventory/products`
**Description**: Adds a new product to the catalog.

**Body**: `ProductCreate`
```json
{
  "sku": "NEW-CABLE-001",
  "name": "New Copper Cable",
  "category": "Power Cable",
  "conductor": "copper",
  "insulation": "XLPE",
  "voltage_kv": 1.1,
  "cores": 4,
  "size_sqmm": 16,
  "application": "feeder",
  "armoured": true,
  "unit_price": 100.0
}
```

### Update Price
**Endpoint**: `POST /inventory/prices`
**Description**: Updates the unit price for a specific SKU.

**Body**: `PriceUpdate`
```json
{
  "sku": "NEW-CABLE-001",
  "unit_price": 120.0
}
```

## 4. System
### Health Check
**Endpoint**: `GET /health` (Note: No `/api/v1` prefix)
**Response**:
```json
{ "status": "ok" }
```


