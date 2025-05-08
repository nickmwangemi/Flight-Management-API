from datetime import datetime
from app import db


class Aircraft(db.Model):
	"""Aircraft model represents a single aircraft in the fleet."""
	id = db.Column(db.Integer, primary_key=True)
	serial_number = db.Column(db.String(64), unique=True, nullable=False)
	manufacturer = db.Column(db.String(128), nullable=False)
	flights = db.relationship('Flight', backref='aircraft', lazy='dynamic')

	def to_dict(self):
		"""Convert object to dictionary for API responses."""
		return {
			'id': self.id,
			'serial_number': self.serial_number,
			'manufacturer': self.manufacturer
		}


class Flight(db.Model):
	"""Flight model represents a scheduled flight."""
	id = db.Column(db.Integer, primary_key=True)
	departure_airport = db.Column(db.String(4), nullable=False)  # ICAO code
	arrival_airport = db.Column(db.String(4), nullable=False)  # ICAO code
	departure_time = db.Column(db.DateTime, nullable=False)
	arrival_time = db.Column(db.DateTime, nullable=False)
	aircraft_id = db.Column(db.Integer, db.ForeignKey('aircraft.id'), nullable=True)

	def to_dict(self):
		"""Convert object to dictionary for API responses."""
		return {
			'id': self.id,
			'departure_airport': self.departure_airport,
			'arrival_airport': self.arrival_airport,
			'departure_time': self.departure_time.isoformat(),
			'arrival_time': self.arrival_time.isoformat(),
			'aircraft_id': self.aircraft_id,
			'aircraft_serial_number': self.aircraft.serial_number if self.aircraft else None
		}
