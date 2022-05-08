import enum
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DeviceStatusEnum(enum.Enum):
    error = 'error'
    open = 'open'
    closed = 'closed'


class Location(db.Model):
    __tablename__ = 'locations'
    id: int = db.Column(db.String(), primary_key=True, default=str(uuid.uuid4()))
    name: str = db.Column(db.String())
    description: str = db.Column(db.String())
    user = db.relationship(db.String(50), db.ForeignKey('user.id'), nullable=True)
    devices = db.relationship('Device', backref='location', lazy=True)

    def __repr__(self):
        return f"<Location: {self.id} - {self.name}>"


class Device(db.Model):
    __tablename__ = 'devices'
    id: int = db.Column(db.String(), primary_key=True, default=str(uuid.uuid4()))
    name: str = db.Column(db.String())
    description: str = db.Column(db.String())
    device_type: str = db.Column(db.String())
    location = db.Column(db.String(50), db.ForeignKey('location.id'), nullable=True)
    status = db.Column(db.Enum(DeviceStatusEnum), default=DeviceStatusEnum.closed, nullable=False)

    def __repr__(self):
        return f"<Device: {self.id} - {self.name}>"

