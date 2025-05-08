from datetime import datetime
from sqlalchemy import func


def validate_icao_code(code):
	"""
	Validate that the provided string is a valid ICAO airport code.
	ICAO codes are 4-letter codes used to identify airports.
	"""
	if not code or not isinstance(code, str):
		return False

	# ICAO codes are 4 alpha characters
	if len(code) != 4 or not code.isalpha():
		return False

	return True


def parse_datetime(dt_str):
	"""Parse a datetime string in ISO format."""
	try:
		return datetime.fromisoformat(dt_str)
	except (ValueError, TypeError):
		return None


def calculate_inflight_time(flight, start_time, end_time):
	"""
	Calculate the in-flight time (in minutes) for a flight that is strictly within
	the given time range.

	Args:
		flight: Flight object
		start_time: Start of the time range
		end_time: End of the time range

	Returns:
		Number of minutes the flight was in the air during the specified time range
	"""
	# Get the actual in-air time within the time range
	flight_start = max(flight.departure_time, start_time)
	flight_end = min(flight.arrival_time, end_time)

	# Check if the flight was in the air during the time range
	if flight_start < flight_end:
		# Calculate minutes
		return (flight_end - flight_start).total_seconds() / 60

	return 0
