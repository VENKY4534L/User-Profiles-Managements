import re
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User

bp = Blueprint("main", __name__)
EMAIL_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")

def validate(payload, require_password=False):
    values = {
        "name": str(payload.get("name", "")).strip(),
        "email": str(payload.get("email", "")).strip().lower(),
        "role": str(payload.get("role", "User")).strip() or "User",
        "password": str(payload.get("password", ""))
    }
    errors = {}
    if not values["name"]:
        errors["name"] = "Name is required."
    elif len(values["name"]) > 100:
        errors["name"] = "Name must be 100 characters or fewer."
    if not EMAIL_RE.match(values["email"]):
        errors["email"] = "Enter a valid email address."
    if len(values["role"]) > 80:
        errors["role"] = "Role must be 80 characters or fewer."
    if require_password and len(values["password"]) < 8:
        errors["password"] = "Password must be at least 8 characters."
    return values, errors

def save_user(payload, user=None, require_password=False):
    values, errors = validate(payload, require_password)
    if errors:
        return None, errors
    user = user or User()
    user.name, user.email, user.role = values["name"], values["email"], values["role"]
    if values["password"]:
        user.set_password(values["password"])
    elif not user.password_hash:
        return None, {"password": "Password is required."}
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None, {"email": "That email address is already registered."}
    return user, {}

def filtered_users(query):
    q = User.query
    if query:
        term = f"%{query}%"
        q = q.filter(db.or_(User.name.ilike(term), User.email.ilike(term), User.role.ilike(term)))
    return q.order_by(User.id.desc()).all()

@bp.get("/")
def index():
    query = request.args.get("q", "").strip()
    return render_template("index.html", users=filtered_users(query), query=query)

@bp.route("/users/new", methods=["GET", "POST"])
def create_user_page():
    if request.method == "POST":
        user, errors = save_user(request.form, require_password=True)
        if user:
            return redirect(url_for("main.user_detail", user_id=user.id))
        return render_template("user_form.html", user=None, errors=errors, form_data=request.form)
    return render_template("user_form.html", user=None, errors={}, form_data={})

@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user_page(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return render_template("not_found.html"), 404
    if request.method == "POST":
        payload = dict(request.form)
        payload["password"] = ""
        updated, errors = save_user(payload, user=user)
        if updated:
            return redirect(url_for("main.user_detail", user_id=updated.id))
        return render_template("user_form.html", user=user, errors=errors, form_data=request.form)
    return render_template("user_form.html", user=user, errors={}, form_data={
        "name": user.name, "email": user.email, "role": user.role
    })

@bp.get("/users/<int:user_id>")
def user_detail(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return render_template("not_found.html"), 404
    return render_template("user_detail.html", user=user)

@bp.post("/users/<int:user_id>/delete")
def delete_user_page(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return render_template("not_found.html"), 404
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("main.index"))

@bp.get("/api/users")
def api_list_users():
    users = filtered_users(request.args.get("q", "").strip())
    return jsonify({"items": [u.to_dict() for u in users], "count": len(users)})

@bp.post("/api/users")
def api_create_user():
    user, errors = save_user(request.get_json(silent=True) or {}, require_password=True)
    if errors:
        return jsonify({"errors": errors}), 400
    return jsonify(user.to_dict()), 201

@bp.get("/api/users/<int:user_id>")
def api_get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user.to_dict())

@bp.route("/api/users/<int:user_id>", methods=["PUT", "PATCH"])
def api_update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    payload = request.get_json(silent=True) or {}
    payload.setdefault("password", "")
    updated, errors = save_user(payload, user=user)
    if errors:
        return jsonify({"errors": errors}), 400
    return jsonify(updated.to_dict())

@bp.delete("/api/users/<int:user_id>")
def api_delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully."})

@bp.get("/health")
def health():
    return jsonify({"status": "ok"})
