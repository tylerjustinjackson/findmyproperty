from app import create_app

# from faker import Faker
import random
from datetime import datetime, timedelta
from app.models import Equipment  # Remove UnclaimedProperty from import
from app import db

# fake = Faker()

app = create_app()

# Configure SQLAlchemy to use unique constraints and handle duplicates
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True  # Helpful for debugging SQL queries


# Add a test route with print statement for debugging
@app.route("/")
def home():
    print("Home route accessed!")  # Debug print
    return "Hello, World! The application is running."


# Add basic error handling
@app.errorhandler(404)
def not_found_error(error):
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500


# Add this temporary route for generating test data
@app.route("/generate-test-data")
def generate_test_data():
    # List of common equipment types
    equipment_types = [
        "Laptop",
        "Monitor",
        "Keyboard",
        "Mouse",
        "Docking Station",
        "Headphones",
        "Webcam",
        "Phone",
        "Tablet",
        "Power Supply",
    ]

    # List of common manufacturers
    manufacturers = [
        "Dell",
        "HP",
        "Lenovo",
        "Apple",
        "Samsung",
        "LG",
        "Logitech",
        "Microsoft",
        "ASUS",
        "Acer",
    ]

    # Generate 20 random items
    # for _ in range(20):
    #     equip_type = random.choice(equipment_types)
    #     manufacturer = random.choice(manufacturers)

    #     equipment = Equipment(
    #         serial_number=fake.unique.ean13(),
    #         manufacturer=manufacturer,
    #         model=f"{manufacturer}-{fake.ean8()}",
    #         equipment_type=equip_type,
    #         purchase_date=fake.date_between(start_date="-5y", end_date="today"),
    #         purchase_price=round(random.uniform(100, 2000), 2),
    #         condition=random.choice(["New", "Good", "Fair", "Poor"]),
    #         notes=fake.text(max_nb_chars=200),
    #     )

    #     db.session.add(equipment)

    # try:
    #     db.session.commit()
    #     return f"Successfully added 20 random equipment items!"
    # except Exception as e:
    #     db.session.rollback()
    #     return f"Error adding items: {str(e)}", 500


if __name__ == "__main__":
    print("Starting Flask application...")  # Debug print
    # app.run(debug=True, host="0.0.0.0", port=5001)  # Changed port to 5001
    app.run()
