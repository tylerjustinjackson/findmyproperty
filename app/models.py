from datetime import datetime
import random
import string
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    legal_name = db.Column(db.String(100))
    employee_id = db.Column(db.String(10), unique=True)
    email = db.Column(db.String(120))
    department = db.Column(db.String(64))
    office_number = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    birthday = db.Column(db.Date)
    bio = db.Column(db.Text)

    # Relationships
    equipment = db.relationship("Equipment", backref="owner", lazy="dynamic")
    history_records = db.relationship("PropertyHistory", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_employee_id():
        while True:
            # Generate a random 6-digit number
            employee_id = "".join(random.choices(string.digits, k=6))
            # Check if it exists
            if not User.query.filter_by(employee_id=employee_id).first():
                return employee_id


class PropertyHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50))  # e.g., "claimed", "released", etc.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # ... any other columns you need ...


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(50))
    manufacturer = db.Column(db.String(100))
    year_manufactured = db.Column(db.Integer)
    purchase_date = db.Column(db.Date)
    msrp = db.Column(db.Float)
    last_maintenance_date = db.Column(db.Date)
    is_decommissioned = db.Column(db.Boolean, default=False)
    decommission_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="claimed")
    release_date = db.Column(db.DateTime)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    employee_id = db.Column(db.String(10))

    # Relationship to PropertyHistory
    history_records = db.relationship(
        "PropertyHistory", backref="equipment", lazy="dynamic"
    )

    @staticmethod
    def generate_property_id():
        """Generate a unique property ID with format: PROP-YYYY-XXXXX"""
        current_year = datetime.now().year

        # Get the last property ID for the current year
        last_equipment = (
            Equipment.query.filter(Equipment.property_id.like(f"PROP-{current_year}-%"))
            .order_by(Equipment.property_id.desc())
            .first()
        )

        if last_equipment:
            # Extract the sequence number and increment
            last_seq = int(last_equipment.property_id.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"PROP-{current_year}-{new_seq:05d}"


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Active")

    # Foreign Keys
    manager_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationships
    manager = db.relationship(
        "User", foreign_keys=[manager_id], backref="managed_projects"
    )
    team_members = db.relationship(
        "User", secondary="project_members", backref="projects"
    )
    equipment = db.relationship(
        "Equipment", secondary="project_equipment", backref="projects"
    )

    @property
    def current_status(self):
        today = datetime.utcnow().date()

        if self.end_date:
            if today > self.end_date.date():
                return "Completed"
            elif today >= self.start_date.date():
                return "Active"
            else:
                return "Scheduled"
        else:
            if today >= self.start_date.date():
                return "Active"
            else:
                return "Scheduled"

    def __repr__(self):
        return f"<Project {self.name}>"


# Association table for project members
project_members = db.Table(
    "project_members",
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
)

# Association table for project equipment
project_equipment = db.Table(
    "project_equipment",
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
    db.Column(
        "equipment_id", db.Integer, db.ForeignKey("equipment.id"), primary_key=True
    ),
)
