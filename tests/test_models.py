import unittest
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Aircraft, Flight
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_aircraft_model(self):
        # Test creating an aircraft
        aircraft = Aircraft(serial_number="ABC123", manufacturer="Boeing")
        db.session.add(aircraft)
        db.session.commit()

        # Test retrieving the aircraft
        saved_aircraft = Aircraft.query.first()
        self.assertEqual(saved_aircraft.serial_number, "ABC123")
        self.assertEqual(saved_aircraft.manufacturer, "Boeing")

        # Test to_dict method
        aircraft_dict = saved_aircraft.to_dict()
        self.assertEqual(aircraft_dict["serial_number"], "ABC123")
        self.assertEqual(aircraft_dict["manufacturer"], "Boeing")

    def test_flight_model(self):
        # Create an aircraft for the flight
        aircraft = Aircraft(serial_number="ABC123", manufacturer="Boeing")
        db.session.add(aircraft)
        db.session.commit()

        # Create a flight
        future_time = datetime.utcnow() + timedelta(days=1)
        later_time = future_time + timedelta(hours=2)

        flight = Flight(
            departure_airport="KJFK",
            arrival_airport="EGLL",
            departure_time=future_time,
            arrival_time=later_time,
            aircraft_id=aircraft.id,
        )
        db.session.add(flight)
        db.session.commit()

        # Test retrieving the flight
        saved_flight = Flight.query.first()
        self.assertEqual(saved_flight.departure_airport, "KJFK")
        self.assertEqual(saved_flight.arrival_airport, "EGLL")
        self.assertEqual(saved_flight.aircraft_id, aircraft.id)

        # Test to_dict method
        flight_dict = saved_flight.to_dict()
        self.assertEqual(flight_dict["departure_airport"], "KJFK")
        self.assertEqual(flight_dict["arrival_airport"], "EGLL")
        self.assertEqual(flight_dict["aircraft_id"], aircraft.id)
        self.assertEqual(flight_dict["aircraft_serial_number"], "ABC123")


if __name__ == "__main__":
    unittest.main()
