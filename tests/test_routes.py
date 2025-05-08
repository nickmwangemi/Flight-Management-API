import json
import unittest
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Aircraft, Flight
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Setup test data
        self.setup_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def setup_test_data(self):
        # Create test aircraft
        aircraft1 = Aircraft(serial_number="TEST001", manufacturer="Airbus")
        aircraft2 = Aircraft(serial_number="TEST002", manufacturer="Boeing")
        db.session.add_all([aircraft1, aircraft2])
        db.session.commit()

        # Create test flights
        future_time = datetime.utcnow() + timedelta(days=1)
        later_time = future_time + timedelta(hours=2)

        flight1 = Flight(
            departure_airport="KJFK",
            arrival_airport="EGLL",
            departure_time=future_time,
            arrival_time=later_time,
            aircraft_id=aircraft1.id,
        )

        flight2 = Flight(
            departure_airport="EGLL",
            arrival_airport="KJFK",
            departure_time=future_time + timedelta(days=1),
            arrival_time=later_time + timedelta(days=1),
            aircraft_id=aircraft2.id,
        )

        db.session.add_all([flight1, flight2])
        db.session.commit()

        self.aircraft1_id = aircraft1.id
        self.aircraft2_id = aircraft2.id
        self.flight1_id = flight1.id
        self.flight2_id = flight2.id

    def test_get_aircraft(self):
        response = self.client.get("/api/aircraft")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["data"]), 2)

    def test_get_aircraft_by_id(self):
        response = self.client.get(f"/api/aircraft/{self.aircraft1_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["serial_number"], "TEST001")

    def test_create_aircraft(self):
        payload = {"serial_number": "NEW001", "manufacturer": "Bombardier"}

        response = self.client.post(
            "/api/aircraft", data=json.dumps(payload), content_type="application/json"
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["serial_number"], "NEW001")

        # Check it was actually added to the database
        aircraft = Aircraft.query.filter_by(serial_number="NEW001").first()
        self.assertIsNotNone(aircraft)

    def test_update_aircraft(self):
        payload = {"manufacturer": "Updated Manufacturer"}

        response = self.client.put(
            f"/api/aircraft/{self.aircraft1_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["manufacturer"], "Updated Manufacturer")

        # Check it was actually updated in the database
        aircraft = Aircraft.query.get(self.aircraft1_id)
        self.assertEqual(aircraft.manufacturer, "Updated Manufacturer")

    def test_delete_aircraft(self):
        # Create a new aircraft without flights for deletion testing
        aircraft = Aircraft(serial_number="DELETE_ME", manufacturer="Test")
        db.session.add(aircraft)
        db.session.commit()

        response = self.client.delete(f"/api/aircraft/{aircraft.id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")

        # Check it was actually deleted from the database
        deleted_aircraft = Aircraft.query.get(aircraft.id)
        self.assertIsNone(deleted_aircraft)

    def test_delete_aircraft_with_flights(self):
        # Try to delete an aircraft that has flights assigned
        response = self.client.delete(f"/api/aircraft/{self.aircraft1_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["status"], "error")

        # Check it was not deleted from the database
        aircraft = Aircraft.query.get(self.aircraft1_id)
        self.assertIsNotNone(aircraft)

    def test_get_flights(self):
        response = self.client.get("/api/flights")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["data"]), 2)

    def test_get_flight_by_id(self):
        response = self.client.get(f"/api/flights/{self.flight1_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["departure_airport"], "KJFK")
        self.assertEqual(data["data"]["arrival_airport"], "EGLL")

    def test_create_flight(self):
        future_time = datetime.utcnow() + timedelta(days=2)
        later_time = future_time + timedelta(hours=3)

        payload = {
            "departure_airport": "EDDF",
            "arrival_airport": "LFPG",
            "departure_time": future_time.isoformat(),
            "arrival_time": later_time.isoformat(),
            "aircraft_id": self.aircraft1_id,
        }

        response = self.client.post(
            "/api/flights", data=json.dumps(payload), content_type="application/json"
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["departure_airport"], "EDDF")
        self.assertEqual(data["data"]["arrival_airport"], "LFPG")

        # Check it was actually added to the database
        flight = Flight.query.filter_by(
            departure_airport="EDDF", arrival_airport="LFPG"
        ).first()
        self.assertIsNotNone(flight)

    def test_create_flight_past_departure(self):
        past_time = datetime.utcnow() - timedelta(hours=1)
        later_time = datetime.utcnow() + timedelta(hours=3)

        payload = {
            "departure_airport": "EDDF",
            "arrival_airport": "LFPG",
            "departure_time": past_time.isoformat(),
            "arrival_time": later_time.isoformat(),
            "aircraft_id": self.aircraft1_id,
        }

        response = self.client.post(
            "/api/flights", data=json.dumps(payload), content_type="application/json"
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["status"], "error")
        self.assertIn("future", data["message"])

    def test_update_flight(self):
        payload = {"arrival_airport": "LFPG"}

        response = self.client.put(
            f"/api/flights/{self.flight1_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["arrival_airport"], "LFPG")

        # Check it was actually updated in the database
        flight = Flight.query.get(self.flight1_id)
        self.assertEqual(flight.arrival_airport, "LFPG")

    def test_delete_flight(self):
        response = self.client.delete(f"/api/flights/{self.flight1_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")

        # Check it was actually deleted from the database
        deleted_flight = Flight.query.get(self.flight1_id)
        self.assertIsNone(deleted_flight)

    def test_assign_aircraft_to_flight(self):
        response = self.client.put(
            f"/api/flights/{self.flight1_id}/assign-aircraft/{self.aircraft2_id}"
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["aircraft_id"], self.aircraft2_id)

        # Check it was actually updated in the database
        flight = Flight.query.get(self.flight1_id)
        self.assertEqual(flight.aircraft_id, self.aircraft2_id)

    def test_search_flights(self):
        # Test search by departure airport
        response = self.client.get("/api/flights?departure_airport=KJFK")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["departure_airport"], "KJFK")

        # Test search by arrival airport
        response = self.client.get("/api/flights?arrival_airport=KJFK")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["arrival_airport"], "KJFK")

    def test_flight_statistics(self):
        # Get current time + buffer to ensure test is predictable
        now = datetime.utcnow()

        # Create flights for testing the statistics endpoint
        future_base = now + timedelta(days=10)

        # Flight 1: 2-hour flight from ABCD to EFGH
        flight1_start = future_base
        flight1_end = future_base + timedelta(hours=2)
        flight1 = Flight(
            departure_airport="ABCD",
            arrival_airport="EFGH",
            departure_time=flight1_start,
            arrival_time=flight1_end,
            aircraft_id=self.aircraft1_id,
        )

        # Flight 2: 3-hour flight from ABCD to WXYZ
        flight2_start = future_base + timedelta(hours=3)
        flight2_end = future_base + timedelta(hours=6)
        flight2 = Flight(
            departure_airport="ABCD",
            arrival_airport="WXYZ",
            departure_time=flight2_start,
            arrival_time=flight2_end,
            aircraft_id=self.aircraft2_id,
        )

        # Flight 3: 2-hour flight from IJKL to MNOP
        flight3_start = future_base + timedelta(hours=1)
        flight3_end = future_base + timedelta(hours=3)
        flight3 = Flight(
            departure_airport="IJKL",
            arrival_airport="MNOP",
            departure_time=flight3_start,
            arrival_time=flight3_end,
            aircraft_id=self.aircraft1_id,
        )

        db.session.add_all([flight1, flight2, flight3])
        db.session.commit()

        # Query for statistics spanning all flights
        start_time = (future_base - timedelta(hours=1)).isoformat()
        end_time = (future_base + timedelta(hours=7)).isoformat()

        response = self.client.get(
            f"/api/reports/flight-stats?start_time={start_time}&end_time={end_time}"
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")

        # Check results
        result = data["data"]
        self.assertEqual(
            len(result), 2
        )  # Should have stats for two departure airports: ABCD and IJKL

        # Find ABCD airport stats
        abcd_stats = next(
            (item for item in result if item["departure_airport"] == "ABCD"), None
        )
        self.assertIsNotNone(abcd_stats)
        self.assertEqual(abcd_stats["flight_count"], 2)

        # Find IJKL airport stats
        ijkl_stats = next(
            (item for item in result if item["departure_airport"] == "IJKL"), None
        )
        self.assertIsNotNone(ijkl_stats)
        self.assertEqual(ijkl_stats["flight_count"], 1)


if __name__ == "__main__":
    unittest.main()
