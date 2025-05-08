"""
Database seeding script for the Aircraft Fleet Management API.
This script populates the database with sample aircraft and flights for development and testing.
"""

import random
import sys
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Aircraft, Flight

# List of aircraft manufacturers and their common models
AIRCRAFT_DATA = [
	{"manufacturer": "Airbus", "models": ["A320", "A330", "A350", "A380"]},
	{"manufacturer": "Boeing", "models": ["737", "747", "777", "787"]},
	{"manufacturer": "Bombardier", "models": ["CRJ700", "CRJ900", "Global 6000"]},
	{"manufacturer": "Embraer", "models": ["E170", "E190", "E195"]},
	{"manufacturer": "Cessna", "models": ["Citation X", "Citation Latitude", "Citation Longitude"]},
]

# List of major airport ICAO codes
AIRPORTS = [
	"KJFK",  # New York JFK
	"KLAX",  # Los Angeles
	"KORD",  # Chicago O'Hare
	"KATL",  # Atlanta
	"EGLL",  # London Heathrow
	"LFPG",  # Paris Charles de Gaulle
	"EDDF",  # Frankfurt
	"LEMD",  # Madrid
	"LIRF",  # Rome Fiumicino
	"EHAM",  # Amsterdam Schiphol
	"VHHH",  # Hong Kong
	"RJTT",  # Tokyo Haneda
	"YSSY",  # Sydney
	"OMDB",  # Dubai
	"ZBAA",  # Beijing Capital
]


def generate_serial_number(manufacturer, model):
	"""Generate a random but realistic-looking serial number."""
	prefix = manufacturer[0] + model.replace(" ", "")[:3].upper()
	number = random.randint(1000, 9999)
	return f"{prefix}-{number}"


def create_aircraft(count=15):
	"""Create and save aircraft to the database."""
	print(f"Creating {count} aircraft...")
	aircraft_list = []

	for _ in range(count):
		# Select a random manufacturer and model
		manufacturer_data = random.choice(AIRCRAFT_DATA)
		manufacturer = manufacturer_data["manufacturer"]
		model = random.choice(manufacturer_data["models"])

		# Generate a unique serial number
		serial_number = generate_serial_number(manufacturer, model)
		while Aircraft.query.filter_by(serial_number=serial_number).first():
			serial_number = generate_serial_number(manufacturer, model)

		# Create full manufacturer string with model
		full_manufacturer = f"{manufacturer} {model}"

		# Create and add the aircraft
		aircraft = Aircraft(serial_number=serial_number, manufacturer=full_manufacturer)
		db.session.add(aircraft)
		aircraft_list.append(aircraft)

	db.session.commit()
	print(f"Created {count} aircraft successfully!")
	return aircraft_list


def generate_flight_time(min_hours=1, max_hours=10):
	"""Generate a random flight duration in hours."""
	return random.uniform(min_hours, max_hours)


def create_flights(aircraft_list, count=50):
	"""Create and save flights to the database."""
	print(f"Creating {count} flights...")
	flight_list = []

	now = datetime.utcnow()

	for _ in range(count):
		# Select random airports
		departure, arrival = random.sample(AIRPORTS, 2)

		# Select a random aircraft (or None for some flights)
		if random.random() < 0.9:  # 90% chance of having an aircraft assigned
			aircraft = random.choice(aircraft_list)
			aircraft_id = aircraft.id
		else:
			aircraft_id = None

		# Generate random future departure time (between tomorrow and 30 days from now)
		days_in_future = random.randint(1, 30)
		hours_in_future = random.randint(0, 23)
		minutes_in_future = random.randint(0, 59)

		departure_time = now + timedelta(
			days=days_in_future,
			hours=hours_in_future,
			minutes=minutes_in_future
		)

		# Generate flight duration and calculate arrival time
		flight_hours = generate_flight_time()
		arrival_time = departure_time + timedelta(hours=flight_hours)

		# Create and add the flight
		flight = Flight(
			departure_airport=departure,
			arrival_airport=arrival,
			departure_time=departure_time,
			arrival_time=arrival_time,
			aircraft_id=aircraft_id
		)
		db.session.add(flight)
		flight_list.append(flight)

	db.session.commit()
	print(f"Created {count} flights successfully!")
	return flight_list


def seed_database(aircraft_count=15, flight_count=50):
	"""Main function to seed the database."""
	print("Starting database seeding...")

	# Check if database already has data
	existing_aircraft = Aircraft.query.count()
	existing_flights = Flight.query.count()

	if existing_aircraft > 0 or existing_flights > 0:
		confirm = input(
			f"Database already contains {existing_aircraft} aircraft and {existing_flights} flights. Do you want to proceed and add more data? (y/n): ")
		if confirm.lower() != 'y':
			print("Database seeding cancelled.")
			return

	try:
		# Create aircraft first
		aircraft_list = create_aircraft(aircraft_count)

		# Then create flights
		create_flights(aircraft_list, flight_count)

		print("Database seeding completed successfully!")

	except Exception as e:
		db.session.rollback()
		print(f"Error seeding database: {str(e)}")
		return


def clear_database():
	"""Clear all data from the database."""
	print("Clearing database...")
	try:
		# Delete flights first to avoid foreign key constraints
		Flight.query.delete()
		Aircraft.query.delete()
		db.session.commit()
		print("Database cleared successfully!")
	except Exception as e:
		db.session.rollback()
		print(f"Error clearing database: {str(e)}")


if __name__ == "__main__":
	app = create_app()
	with app.app_context():
		# Check for command line arguments
		if len(sys.argv) > 1 and sys.argv[1] == '--clear':
			clear_database()
			if len(sys.argv) <= 2 or sys.argv[2] != '--only-clear':
				seed_database()
		else:
			# Default behavior: just seed the database
			seed_database()