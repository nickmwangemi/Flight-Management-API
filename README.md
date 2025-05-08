# Aircraft Fleet Management API

A REST API for efficiently managing an aircraft fleet, including CRUD operations for aircraft and flights, and comprehensive reporting capabilities.

## Features

- 🛩️ Aircraft management (create, read, update, delete)
- ✈️ Flight management with aircraft assignment
- 🔍 Search flights by departure/arrival airports and time ranges
- 📊 Generate flight statistics reports by time period
- 🧪 Comprehensive test suite

## Requirements

- Python 3.6+
- Flask
- SQLAlchemy
- Additional dependencies in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:nickmwangemi/Flight-Management-API.git
   cd aircraft-fleet-management
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   flask run
   ```

5. Run tests:
   ```bash
   python -m unittest discover
   ```

## API Documentation

### Aircraft Endpoints

#### GET /api/aircraft
Get all aircraft in the fleet.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "serial_number": "ABC123",
      "manufacturer": "Boeing"
    },
    ...
  ]
}
```

#### GET /api/aircraft/{id}
Get a specific aircraft by ID.

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "serial_number": "ABC123",
    "manufacturer": "Boeing"
  }
}
```

#### POST /api/aircraft
Create a new aircraft.

**Request Body:**
```json
{
  "serial_number": "ABC123",
  "manufacturer": "Boeing"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Aircraft created successfully",
  "data": {
    "id": 1,
    "serial_number": "ABC123",
    "manufacturer": "Boeing"
  }
}
```

#### PUT /api/aircraft/{id}
Update an existing aircraft.

**Request Body:**
```json
{
  "manufacturer": "Airbus"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Aircraft updated successfully",
  "data": {
    "id": 1,
    "serial_number": "ABC123",
    "manufacturer": "Airbus"
  }
}
```

#### DELETE /api/aircraft/{id}
Delete an aircraft by ID.

**Response:**
```json
{
  "status": "success",
  "message": "Aircraft deleted successfully"
}
```

### Flight Endpoints

#### GET /api/flights
Get flights with optional filtering by departure/arrival airport and departure time range.

**Query Parameters:**
- `departure_airport`: Filter by departure airport ICAO code
- `arrival_airport`: Filter by arrival airport ICAO code
- `departure_after`: Filter for flights departing after this datetime (ISO format)
- `departure_before`: Filter for flights departing before this datetime (ISO format)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "departure_airport": "KJFK",
      "arrival_airport": "EGLL",
      "departure_time": "2025-05-09T12:00:00",
      "arrival_time": "2025-05-09T20:00:00",
      "aircraft_id": 1,
      "aircraft_serial_number": "ABC123"
    },
    ...
  ]
}
```

#### GET /api/flights/{id}
Get a specific flight by ID.

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "departure_airport": "KJFK",
    "arrival_airport": "EGLL",
    "departure_time": "2025-05-09T12:00:00",
    "arrival_time": "2025-05-09T20:00:00",
    "aircraft_id": 1,
    "aircraft_serial_number": "ABC123"
  }
}
```

#### POST /api/flights
Create a new flight.

**Request Body:**
```json
{
  "departure_airport": "KJFK",
  "arrival_airport": "EGLL",
  "departure_time": "2025-05-09T12:00:00",
  "arrival_time": "2025-05-09T20:00:00",
  "aircraft_id": 1  // Optional
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Flight created successfully",
  "data": {
    "id": 1,
    "departure_airport": "KJFK",
    "arrival_airport": "EGLL",
    "departure_time": "2025-05-09T12:00:00",
    "arrival_time": "2025-05-09T20:00:00",
    "aircraft_id": 1,
    "aircraft_serial_number": "ABC123"
  }
}
```

#### PUT /api/flights/{id}
Update an existing flight.

**Request Body:**
```json
{
  "arrival_airport": "LFPG"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Flight updated successfully",
  "data": {
    "id": 1,
    "departure_airport": "KJFK",
    "arrival_airport": "LFPG",
    "departure_time": "2025-05-09T12:00:00",
    "arrival_time": "2025-05-09T20:00:00",
    "aircraft_id": 1,
    "aircraft_serial_number": "ABC123"
  }
}
```

#### DELETE /api/flights/{id}
Delete a flight by ID.

**Response:**
```json
{
  "status": "success",
  "message": "Flight deleted successfully"
}
```

#### PUT /api/flights/{flight_id}/assign-aircraft/{aircraft_id}
Assign an aircraft to a flight.

**Response:**
```json
{
  "status": "success",
  "message": "Aircraft 'ABC123' assigned to flight 1",
  "data": {
    "id": 1,
    "departure_airport": "KJFK",
    "arrival_airport": "EGLL",
    "departure_time": "2025-05-09T12:00:00",
    "arrival_time": "2025-05-09T20:00:00",
    "aircraft_id": 1,
    "aircraft_serial_number": "ABC123"
  }
}
```

### Reporting Endpoints

#### GET /api/reports/flight-stats
Generate flight statistics report for a given time period.

**Query Parameters:**
- `start_time`: Start of the time range (ISO format)
- `end_time`: End of the time range (ISO format)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "departure_airport": "KJFK",
      "flight_count": 5,
      "aircraft_flight_times": [
        {
          "aircraft_id": 1,
          "serial_number": "ABC123",
          "in_flight_minutes": 240.5
        },
        {
          "aircraft_id": 2,
          "serial_number": "XYZ789",
          "in_flight_minutes": 180.25
        }
      ],
      "average_flight_time": 210.38
    },
    ...
  ],
  "meta": {
    "start_time": "2025-05-01T00:00:00",
    "end_time": "2025-05-31T23:59:59",
    "total_airports": 3,
    "total_flights": 12
  }
}
```

## Constraints & Validations

1. Aircraft are identified by unique serial numbers
2. Flights must have a future departure time
3. Arrival time must be after departure time
4. Airport codes must be valid ICAO codes (4 letters)
5. Aircraft can only be deleted if not assigned to any flights

## Technical Implementation

- Built with Flask for the web framework
- SQLAlchemy for ORM and database operations
- SQLite for local development database
- Unit tests with Python's unittest framework
- RESTful API design principles

## Future Enhancements

- Authentication and authorization
- Pagination for large datasets
- Additional reporting capabilities
- Real-time flight tracking
- Integration with external aviation APIs

# Database Seeding

I've created a database seeding script (`seed_db.py`) that will populate your database with sample data for development and testing purposes. Here's how to use it:

## Features

- Creates a configurable number of aircraft with realistic manufacturer and model combinations
- Generates unique serial numbers for each aircraft
- Creates flights between major international airports with realistic departure/arrival times
- Assigns aircraft to flights (with some flights intentionally left unassigned)
- Handles database clearing and re-seeding

## Usage

### Basic Seeding

To populate your database with default values (15 aircraft and 50 flights):

```bash
python seed_db.py
```

### Clear and Re-seed

To clear the existing data and re-seed the database:

```bash
python seed_db.py --clear
```

### Only Clear

To clear the database without adding new seed data:

```bash
python seed_db.py --clear --only-clear
```

### Customizing Seed Data

You can modify the `seed_database()` function call in the script to customize the number of aircraft and flights:

```python
# To create 20 aircraft and 100 flights
seed_database(aircraft_count=20, flight_count=100)
```

## Sample Data Generated

### Aircraft

- Manufacturers include: Airbus, Boeing, Bombardier, Embraer, and Cessna
- Models appropriate to each manufacturer (e.g., Boeing 737, Airbus A320)
- Unique serial numbers in the format `[Manufacturer Initial][Model Code]-[4-digit number]`

### Flights

- Randomly selected departure and arrival airports from a list of major international airports
- Departure times within the next 30 days
- Realistic flight durations
- 90% of flights have aircraft assigned; 10% are unassigned

## Integration with the Application

This seeding script uses your existing application context and models, so it's fully integrated with your Flask application. You can run it independently or integrate it into your application startup process for development environments.