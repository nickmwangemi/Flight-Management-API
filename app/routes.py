from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import and_, func, or_

from app import db
from app.models import Aircraft, Flight
from app.utils import calculate_inflight_time, parse_datetime, validate_icao_code

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ----- Aircraft Endpoints -----


@api_bp.route("/aircraft", methods=["GET"])
def get_aircraft():
    """Get all aircraft in the fleet."""
    aircraft = Aircraft.query.all()
    return jsonify({"status": "success", "data": [a.to_dict() for a in aircraft]}), 200


@api_bp.route("/aircraft/<int:aircraft_id>", methods=["GET"])
def get_aircraft_by_id(aircraft_id):
    """Get a specific aircraft by ID."""
    aircraft = Aircraft.query.get_or_404(aircraft_id)
    return jsonify({"status": "success", "data": aircraft.to_dict()}), 200


@api_bp.route("/aircraft", methods=["POST"])
def create_aircraft():
    """Create a new aircraft."""
    data = request.get_json() or {}

    # Validate required fields
    if "serial_number" not in data or "manufacturer" not in data:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Missing required fields: serial_number and manufacturer",
                }
            ),
            400,
        )

    # Check if aircraft with this serial number already exists
    if Aircraft.query.filter_by(serial_number=data["serial_number"]).first():
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Aircraft with serial number '{data['serial_number']}' already exists",
                }
            ),
            409,
        )

    # Create new Aircraft
    aircraft = Aircraft(
        serial_number=data["serial_number"], manufacturer=data["manufacturer"]
    )

    db.session.add(aircraft)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "message": "Aircraft created successfully",
                "data": aircraft.to_dict(),
            }
        ),
        201,
    )


@api_bp.route("/aircraft/<int:aircraft_id>", methods=["PUT"])
def update_aircraft(aircraft_id):
    """Update an existing aircraft."""
    aircraft = Aircraft.query.get_or_404(aircraft_id)
    data = request.get_json() or {}

    # Update fields if provided
    if "serial_number" in data:
        # Check if new serial number conflicts with another aircraft
        existing = Aircraft.query.filter_by(serial_number=data["serial_number"]).first()
        if existing and existing.id != aircraft_id:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Aircraft with serial number '{data['serial_number']}' already exists",
                    }
                ),
                409,
            )
        aircraft.serial_number = data["serial_number"]

    if "manufacturer" in data:
        aircraft.manufacturer = data["manufacturer"]

    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "message": "Aircraft updated successfully",
                "data": aircraft.to_dict(),
            }
        ),
        200,
    )


@api_bp.route("/aircraft/<int:aircraft_id>", methods=["DELETE"])
def delete_aircraft(aircraft_id):
    """Delete an aircraft by ID."""
    aircraft = Aircraft.query.get_or_404(aircraft_id)

    # Check if aircraft is assigned to any flights
    if Flight.query.filter_by(aircraft_id=aircraft_id).first():
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Cannot delete aircraft that is assigned to flights",
                }
            ),
            400,
        )

    db.session.delete(aircraft)
    db.session.commit()

    return (
        jsonify({"status": "success", "message": "Aircraft deleted successfully"}),
        200,
    )


# ----- Flight Endpoints -----


@api_bp.route("/flights", methods=["GET"])
def get_flights():
    """
    Get flights with optional filtering by departure/arrival airport and departure time range.

    Query Parameters:
    - departure_airport: Filter by departure airport ICAO code
    - arrival_airport: Filter by arrival airport ICAO code
    - departure_after: Filter for flights departing after this datetime (ISO format)
    - departure_before: Filter for flights departing before this datetime (ISO format)
    """
    # Start with base query
    query = Flight.query

    # Apply filters if provided
    departure_airport = request.args.get("departure_airport")
    arrival_airport = request.args.get("arrival_airport")
    departure_after = request.args.get("departure_after")
    departure_before = request.args.get("departure_before")

    if departure_airport:
        if not validate_icao_code(departure_airport):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid ICAO code: {departure_airport}",
                    }
                ),
                400,
            )
        query = query.filter_by(departure_airport=departure_airport.upper())

    if arrival_airport:
        if not validate_icao_code(arrival_airport):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid ICAO code: {arrival_airport}",
                    }
                ),
                400,
            )
        query = query.filter_by(arrival_airport=arrival_airport.upper())

    if departure_after:
        dt = parse_datetime(departure_after)
        if not dt:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid datetime format for departure_after: {departure_after}",
                    }
                ),
                400,
            )
        query = query.filter(Flight.departure_time >= dt)

    if departure_before:
        dt = parse_datetime(departure_before)
        if not dt:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid datetime format for departure_before: {departure_before}",
                    }
                ),
                400,
            )
        query = query.filter(Flight.departure_time <= dt)

    flights = query.all()
    return jsonify({"status": "success", "data": [f.to_dict() for f in flights]}), 200


@api_bp.route("/flights/<int:flight_id>", methods=["GET"])
def get_flight_by_id(flight_id):
    """Get a specific flight by ID."""
    flight = Flight.query.get_or_404(flight_id)
    return jsonify({"status": "success", "data": flight.to_dict()}), 200


@api_bp.route("/flights", methods=["POST"])
def create_flight():
    """Create a new flight."""
    data = request.get_json() or {}

    # Validate required fields
    required_fields = [
        "departure_airport",
        "arrival_airport",
        "departure_time",
        "arrival_time",
    ]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}",
                }
            ),
            400,
        )

    # Validate ICAO codes
    if not validate_icao_code(data["departure_airport"]):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Invalid departure airport ICAO code: {data['departure_airport']}",
                }
            ),
            400,
        )

    if not validate_icao_code(data["arrival_airport"]):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Invalid arrival airport ICAO code: {data['arrival_airport']}",
                }
            ),
            400,
        )

    # Parse datetime strings
    departure_time = parse_datetime(data["departure_time"])
    arrival_time = parse_datetime(data["arrival_time"])

    if not departure_time:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Invalid departure_time format: {data['departure_time']}",
                }
            ),
            400,
        )

    if not arrival_time:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Invalid arrival_time format: {data['arrival_time']}",
                }
            ),
            400,
        )

    # Validate that departure is in the future
    now = datetime.utcnow()
    if departure_time <= now:
        return (
            jsonify(
                {"status": "error", "message": "Departure time must be in the future"}
            ),
            400,
        )

    # Validate that arrival is after departure
    if arrival_time <= departure_time:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Arrival time must be after departure time",
                }
            ),
            400,
        )

    # Check if aircraft exists (if provided)
    aircraft_id = data.get("aircraft_id")
    if aircraft_id:
        aircraft = Aircraft.query.get(aircraft_id)
        if not aircraft:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Aircraft with ID {aircraft_id} not found",
                    }
                ),
                404,
            )

    # Create new Flight
    flight = Flight(
        departure_airport=data["departure_airport"].upper(),
        arrival_airport=data["arrival_airport"].upper(),
        departure_time=departure_time,
        arrival_time=arrival_time,
        aircraft_id=aircraft_id,
    )

    db.session.add(flight)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "message": "Flight created successfully",
                "data": flight.to_dict(),
            }
        ),
        201,
    )


@api_bp.route("/flights/<int:flight_id>", methods=["PUT"])
def update_flight(flight_id):
    """Update an existing flight."""
    flight = Flight.query.get_or_404(flight_id)
    data = request.get_json() or {}

    # If updating departure time, check that it's in the future
    if "departure_time" in data:
        departure_time = parse_datetime(data["departure_time"])
        if not departure_time:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid departure_time format: {data['departure_time']}",
                    }
                ),
                400,
            )

        now = datetime.utcnow()
        if departure_time <= now:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Departure time must be in the future",
                    }
                ),
                400,
            )

        flight.departure_time = departure_time

    # If updating arrival time, check that it's after departure time
    if "arrival_time" in data:
        arrival_time = parse_datetime(data["arrival_time"])
        if not arrival_time:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid arrival_time format: {data['arrival_time']}",
                    }
                ),
                400,
            )

        departure = flight.departure_time
        if "departure_time" in data:
            departure = parse_datetime(data["departure_time"])

        if arrival_time <= departure:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Arrival time must be after departure time",
                    }
                ),
                400,
            )

        flight.arrival_time = arrival_time

    # Update ICAO codes if provided
    if "departure_airport" in data:
        if not validate_icao_code(data["departure_airport"]):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid departure airport ICAO code: {data['departure_airport']}",
                    }
                ),
                400,
            )
        flight.departure_airport = data["departure_airport"].upper()

    if "arrival_airport" in data:
        if not validate_icao_code(data["arrival_airport"]):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Invalid arrival airport ICAO code: {data['arrival_airport']}",
                    }
                ),
                400,
            )
        flight.arrival_airport = data["arrival_airport"].upper()

    # Update aircraft assignment if provided
    if "aircraft_id" in data:
        if data["aircraft_id"] is not None:
            aircraft = Aircraft.query.get(data["aircraft_id"])
            if not aircraft:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Aircraft with ID {data['aircraft_id']} not found",
                        }
                    ),
                    404,
                )
        flight.aircraft_id = data["aircraft_id"]

    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "message": "Flight updated successfully",
                "data": flight.to_dict(),
            }
        ),
        200,
    )


@api_bp.route("/flights/<int:flight_id>", methods=["DELETE"])
def delete_flight(flight_id):
    """Delete a flight by ID."""
    flight = Flight.query.get_or_404(flight_id)

    db.session.delete(flight)
    db.session.commit()

    return jsonify({"status": "success", "message": "Flight deleted successfully"}), 200


@api_bp.route(
    "/flights/<int:flight_id>/assign-aircraft/<int:aircraft_id>", methods=["PUT"]
)
def assign_aircraft_to_flight(flight_id, aircraft_id):
    """Assign an aircraft to a flight."""
    flight = Flight.query.get_or_404(flight_id)
    aircraft = Aircraft.query.get_or_404(aircraft_id)

    flight.aircraft_id = aircraft.id
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "message": f"Aircraft '{aircraft.serial_number}' assigned to flight {flight_id}",
                "data": flight.to_dict(),
            }
        ),
        200,
    )


@api_bp.route("/reports/flight-stats", methods=["GET"])
def flight_statistics():
    """
    Generate flight statistics report for a given time period.

    Query Parameters:
    - start_time: Start of the time range (ISO format)
    - end_time: End of the time range (ISO format)

    Returns statistics grouped by departure airport including:
    - Number of flights
    - Average in-flight time (in minutes) within the specified time range
    """
    start_time_str = request.args.get("start_time")
    end_time_str = request.args.get("end_time")

    if not start_time_str or not end_time_str:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Both start_time and end_time are required",
                }
            ),
            400,
        )

    start_time = parse_datetime(start_time_str)
    end_time = parse_datetime(end_time_str)

    if not start_time or not end_time:
        return jsonify({"status": "error", "message": "Invalid datetime format"}), 400

    if end_time <= start_time:
        return (
            jsonify(
                {"status": "error", "message": "end_time must be after start_time"}
            ),
            400,
        )

    # Find flights that are at least partially within the time range
    flights = Flight.query.filter(
        or_(
            # Flight starts within the range
            and_(
                Flight.departure_time >= start_time, Flight.departure_time <= end_time
            ),
            # Flight ends within the range
            and_(Flight.arrival_time >= start_time, Flight.arrival_time <= end_time),
            # Flight completely spans the range
            and_(Flight.departure_time <= start_time, Flight.arrival_time >= end_time),
        )
    ).all()

    # Group flights by departure airport
    stats = {}
    for flight in flights:
        departure_airport = flight.departure_airport

        if departure_airport not in stats:
            stats[departure_airport] = {
                "flight_count": 0,
                "aircraft_flight_times": {},
                "total_flight_time": 0,
            }

        stats[departure_airport]["flight_count"] += 1

        # Calculate in-flight time within the specified range
        if flight.aircraft_id:
            in_flight_minutes = calculate_inflight_time(flight, start_time, end_time)

            aircraft_id = flight.aircraft_id
            if aircraft_id not in stats[departure_airport]["aircraft_flight_times"]:
                stats[departure_airport]["aircraft_flight_times"][aircraft_id] = 0

            stats[departure_airport]["aircraft_flight_times"][
                aircraft_id
            ] += in_flight_minutes
            stats[departure_airport]["total_flight_time"] += in_flight_minutes

    # Format the response
    result = []
    for airport, data in stats.items():
        airport_data = {
            "departure_airport": airport,
            "flight_count": data["flight_count"],
            "aircraft_flight_times": [],
            "average_flight_time": 0,
        }

        # Calculate average flight time
        if data["flight_count"] > 0:
            airport_data["average_flight_time"] = round(
                data["total_flight_time"] / data["flight_count"], 2
            )

        # Add individual aircraft flight times
        for aircraft_id, minutes in data["aircraft_flight_times"].items():
            aircraft = Aircraft.query.get(aircraft_id)
            airport_data["aircraft_flight_times"].append(
                {
                    "aircraft_id": aircraft_id,
                    "serial_number": aircraft.serial_number if aircraft else "Unknown",
                    "in_flight_minutes": round(minutes, 2),
                }
            )

        result.append(airport_data)

    return (
        jsonify(
            {
                "status": "success",
                "data": result,
                "meta": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "total_airports": len(result),
                    "total_flights": sum(d["flight_count"] for d in result),
                },
            }
        ),
        200,
    )
