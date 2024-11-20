from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, login
from app.models import User, Equipment, PropertyHistory, Project
from datetime import datetime
from werkzeug.urls import url_parse
from flask import abort

routes_bp = Blueprint("routes", __name__)

PROPERTY_TYPES = [
    "Laptop",
    "Desktop Computer",
    "Monitor",
    "Tablet",
    "Smartphone",
    "Printer",
    "Scanner",
    "Server",
    "Network Equipment",
    "Camera",
    "Projector",
    "Television",
    "Audio Equipment",
    "Office Furniture",
    "Tools",
    "Laboratory Equipment",
    "Safety Equipment",
    "Vehicle",
    "Software License",
    "Other",
]


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@routes_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.equipment"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password")
            return redirect(url_for("routes.login"))

        login_user(user)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("routes.equipment")
        return redirect(next_page)

    return render_template("login.html")


@routes_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("routes.login"))


@routes_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("routes.equipment"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        legal_name = request.form.get("legal_name")

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("routes.register"))

        user = User(username=username, legal_name=legal_name)
        user.set_password(password)
        user.employee_id = User.generate_employee_id()

        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful!")
            return redirect(url_for("routes.login"))
        except Exception as e:
            db.session.rollback()
            flash("Error during registration")
            return redirect(url_for("routes.register"))

    return render_template("register.html")


@routes_bp.route("/")
@routes_bp.route("/equipment")
@login_required
def equipment():
    search_query = request.args.get("search", "").strip()

    query = Equipment.query.filter_by(user_id=current_user.id)

    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Equipment.name.ilike(search),
                Equipment.property_type.ilike(search),
                Equipment.manufacturer.ilike(search),
            )
        )

    equipment_list = query.order_by(Equipment.id.desc()).all()
    return render_template(
        "equipment.html", equipment=equipment_list, search_query=search_query
    )


@routes_bp.route("/unclaimed_property")
@login_required
def unclaimed_property():
    search_query = request.args.get("search", "").strip()
    query = Equipment.query.filter_by(user_id=None)

    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Equipment.name.ilike(search),
                Equipment.property_type.ilike(search),
                Equipment.manufacturer.ilike(search),
            )
        )

    equipment_list = query.order_by(Equipment.id.desc()).all()
    return render_template(
        "unclaimed_property.html", equipment=equipment_list, search_query=search_query
    )


@routes_bp.route("/equipment/add", methods=["GET", "POST"])
@login_required
def add_equipment():
    if request.method == "POST":
        try:
            equipment = Equipment(
                property_id=Equipment.generate_property_id(),
                name=request.form.get("name"),
                property_type=request.form.get("property_type"),
                manufacturer=request.form.get("manufacturer"),
                year_manufactured=request.form.get("year_manufactured"),
                msrp=float(request.form.get("msrp") or 0),
                user_id=current_user.id,
                employee_id=current_user.employee_id,
            )
            db.session.add(equipment)
            db.session.commit()
            flash("Equipment added successfully!")
            return redirect(url_for("routes.equipment"))
        except Exception as e:
            db.session.rollback()
            flash("Error adding equipment")
            return redirect(url_for("routes.add_equipment"))

    return render_template("add_equipment.html", property_types=PROPERTY_TYPES)


@routes_bp.route("/equipment/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_equipment(id):
    equipment = Equipment.query.get_or_404(id)
    if equipment.user_id != current_user.id:
        flash("You cannot edit this equipment")
        return redirect(url_for("routes.equipment"))

    if request.method == "POST":
        try:
            equipment.name = request.form.get("name")
            equipment.property_type = request.form.get("property_type")
            equipment.manufacturer = request.form.get("manufacturer")
            equipment.year_manufactured = request.form.get("year_manufactured")
            equipment.msrp = float(request.form.get("msrp") or 0)
            db.session.commit()
            flash("Equipment updated successfully!")
            return redirect(url_for("routes.equipment"))
        except Exception as e:
            db.session.rollback()
            flash("Error updating equipment")

    return render_template(
        "edit_equipment.html", equipment=equipment, property_types=PROPERTY_TYPES
    )


@routes_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        try:
            current_user.legal_name = request.form.get("legal_name")
            current_user.email = request.form.get("email")
            current_user.department = request.form.get("department")
            db.session.commit()
            flash("Profile updated successfully!")
        except Exception as e:
            db.session.rollback()
            flash("Error updating profile")

    return render_template("profile.html")


@routes_bp.route("/property_history/<int:id>")
@login_required
def property_history(id):
    equipment = Equipment.query.filter_by(id=id).first_or_404()
    history = equipment.history_records.order_by(PropertyHistory.timestamp.desc()).all()
    return render_template(
        "property_history.html", equipment=equipment, history=history
    )


@routes_bp.route("/claim_property/<int:id>", methods=["POST"])
@login_required
def claim_property(id):
    equipment = Equipment.query.get_or_404(id)
    if equipment.user_id is not None:
        flash("This equipment is already claimed")
        return redirect(url_for("routes.unclaimed_property"))

    try:
        equipment.user_id = current_user.id
        equipment.employee_id = current_user.employee_id
        db.session.commit()
        flash("Equipment claimed successfully!")
    except Exception as e:
        db.session.rollback()
        flash("Error claiming equipment")

    return redirect(url_for("routes.equipment"))


@routes_bp.route("/release_property/<int:id>", methods=["POST"])
@login_required
def release_property(id):
    equipment = Equipment.query.get_or_404(id)
    if equipment.user_id != current_user.id:
        flash("You cannot release this equipment")
        return redirect(url_for("routes.equipment"))

    try:
        equipment.user_id = None
        equipment.employee_id = None
        db.session.commit()
        flash("Equipment released successfully!")
    except Exception as e:
        db.session.rollback()
        flash("Error releasing equipment")

    return redirect(url_for("routes.equipment"))


@routes_bp.route("/projects")
@login_required
def projects():
    # Get projects where user is either manager or team member
    user_projects = Project.query.filter(
        db.or_(
            Project.manager_id == current_user.id,
            Project.team_members.any(id=current_user.id),
        )
    ).all()
    return render_template("projects.html", projects=user_projects)


@routes_bp.route("/project/<int:id>")
@login_required
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template("project_detail.html", project=project)


@routes_bp.route("/project/add", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        try:
            project = Project(
                name=request.form.get("name"),
                description=request.form.get("description"),
                start_date=datetime.strptime(
                    request.form.get("start_date"), "%Y-%m-%d"
                ),
                end_date=(
                    datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
                    if request.form.get("end_date")
                    else None
                ),
                status="Active",
                manager_id=current_user.id,
            )

            # Add selected team members
            selected_members = request.form.getlist("team_members")
            if selected_members:
                members = User.query.filter(User.id.in_(selected_members)).all()
                project.team_members.extend(members)

            db.session.add(project)
            db.session.commit()
            flash("Project added successfully!")
            return redirect(url_for("routes.projects"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding project: {str(e)}")
            return redirect(url_for("routes.add_project"))

    # Get all users except current user for team member selection
    available_users = User.query.filter(User.id != current_user.id).all()
    return render_template("add_project.html", users=available_users)


@routes_bp.route("/project/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    if current_user != project.manager:
        abort(403)

    db.session.delete(project)
    db.session.commit()

    flash("Project has been deleted.")
    return redirect(url_for("routes.projects"))


@routes_bp.route("/property/<int:id>/delete", methods=["POST"])
@login_required
def delete_property(id):
    # Check if user is tylerjackson
    if current_user.username != "tylerjackson":
        flash("You do not have permission to delete properties.", "error")
        return redirect(url_for("routes.unclaimed_property"))

    property = Equipment.query.get_or_404(id)
    db.session.delete(property)
    db.session.commit()

    flash("Property has been deleted successfully.", "success")
    return redirect(url_for("routes.unclaimed_property"))
