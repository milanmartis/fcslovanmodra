import os
import uuid
from datetime import datetime
from flask import (
    Blueprint, render_template, request, jsonify,
    current_app, redirect, url_for, flash
)
from flask_login import login_required
# from flask_security import roles_required
from werkzeug.utils import secure_filename

from app import db
from app.models import Sponsor
from app.posts.routes import s3_client, s3_extra_args, BUCKET_NAME, s3_presign
from app.main.routes import Next, RightColumn
from app import csrf
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
from flask import abort
def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return deco

sponsors_bp = Blueprint("sponsors", __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def make_sponsor_key(filename: str) -> str:
    return f"sponsors/{filename}"


# ---------- PUBLIC STRÁNKA SPONZOROV ----------

@sponsors_bp.route("/sponsors")
def sponsors_public():
    main_sponsors = (
        Sponsor.query
        .filter_by(kind="main")
        .order_by(Sponsor.orderz.asc())
        .all()
    )
    partners = (
        Sponsor.query
        .filter_by(kind="partner")
        .order_by(Sponsor.orderz.asc())
        .all()
    )

    main_sponsors_data = []
    for s in main_sponsors:
        key = make_sponsor_key(s.image_file)
        main_sponsors_data.append({
            "id": s.id,
            "name": s.name or "",
            "url": s.url or "",
            "image_url": s3_presign(key),
        })

    partners_data = []
    for s in partners:
        key = make_sponsor_key(s.image_file)
        partners_data.append({
            "id": s.id,
            "name": s.name or "",
            "url": s.url or "",
            "image_url": s3_presign(key),
        })

    return render_template(
        "sponsors/sponsors.html",
        main_sponsors=main_sponsors_data,
        partners=partners_data,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )

# ---------- ADMIN STRÁNKA (len HTML, dáta idú cez JS) ----------

@sponsors_bp.route("/admin/sponsors", methods=["GET"])
@login_required
@roles_required('Admin', 'WebAdmin')
def sponsors_admin():
    return render_template(
        "sponsors/sponsors_admin.html",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )



@sponsors_bp.route("/admin/sponsors/<int:sponsor_id>", methods=["PUT"])
@csrf.exempt
@login_required
@roles_required('Admin', 'WebAdmin')
def sponsors_update_info(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    data = request.get_json(silent=True) or {}

    sponsor.name = data.get("name", "") or ""
    sponsor.url = data.get("url", "") or ""
    sponsor.describe = data.get("describe", "") or ""

    db.session.commit()
    return jsonify({"message": "Sponsor updated"}), 200

# ---------- JSON API PRE GALÉRIU (HLAVNÍ / PARTNERI) ----------

def _validate_kind(kind: str) -> str:
    if kind not in ("main", "partner"):
        raise ValueError("Invalid kind")
    return kind


@sponsors_bp.route("/admin/sponsors/images/<kind>", methods=["GET"])
@login_required
@roles_required('Admin', 'WebAdmin')
def sponsors_images(kind):
    try:
        kind = _validate_kind(kind)
    except ValueError:
        return jsonify({"error": "Invalid kind"}), 400

    sponsors = (
        Sponsor.query
        .filter_by(kind=kind)
        .order_by(Sponsor.orderz.asc())
        .all()
    )

    data = []
    for s in sponsors:
        key = make_sponsor_key(s.image_file)
        image_url = s3_presign(key)
        data.append({
            "id": s.id,
            "name": s.name or "",
            "url": s.url or "",
            "orderz": s.orderz,
            "describe": s.describe or "",
            "image_url": image_url,
        })

    return jsonify(data)


@sponsors_bp.route("/admin/sponsors/images/<kind>/upload", methods=["PUT"])
@csrf.exempt
@login_required
@roles_required('Admin', 'WebAdmin')
def sponsors_upload(kind):
    try:
        kind = _validate_kind(kind)
    except ValueError:
        return jsonify({"error": "Invalid kind"}), 400

    file = request.files.get("image_file2")
    if not file or not getattr(file, "filename", ""):
        return jsonify({"error": "No file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        original = secure_filename(file.filename)
        base, ext = os.path.splitext(original)
        new_filename = f"{uuid.uuid4().hex}_{base}{ext.lower()}"
        s3_key = make_sponsor_key(new_filename)

        # upload do S3
        s3_client().upload_fileobj(
            file,
            BUCKET_NAME,
            s3_key,
            ExtraArgs=s3_extra_args(file),
        )

        # orderz = posledné + 1 v rámci daného kind
        max_order = (
            db.session.query(db.func.max(Sponsor.orderz))
            .filter(Sponsor.kind == kind)
            .scalar()
        )
        next_order = (max_order or 0) + 1

        sponsor = Sponsor(
            name="",
            url="",
            kind=kind,
            image_file=new_filename,
            orderz=next_order,
        )
        db.session.add(sponsor)
        db.session.commit()

        return jsonify({"message": "Image uploaded", "id": sponsor.id}), 200

    except Exception as e:
        current_app.logger.exception("Error in sponsors_upload: %s", e)
        db.session.rollback()
        return jsonify({"error": "Upload failed"}), 500


@sponsors_bp.route("/admin/sponsors/images/delete/<int:sponsor_id>", methods=["DELETE"])
@csrf.exempt
@login_required
@roles_required('Admin', 'WebAdmin')
def sponsors_delete_image(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)

    try:
        # zmazať zo S3
        s3_client().delete_object(
            Bucket=BUCKET_NAME,
            Key=make_sponsor_key(sponsor.image_file)
        )
    except Exception as e:
        current_app.logger.warning("S3 delete failed (sponsor): %s", e)

    db.session.delete(sponsor)
    db.session.commit()
    return jsonify({"message": "Sponzor vymazaný"}), 200


@sponsors_bp.route("/admin/sponsors/images/update_order", methods=["POST"])
@csrf.exempt
@login_required
@roles_required('Admin', 'WebAdmin')
def sponsors_update_order():
    data = request.json or []

    if not isinstance(data, list):
        return jsonify({"error": "Bad payload"}), 400

    ids = [item.get("id") for item in data if "id" in item]
    if not ids:
        return jsonify({"error": "No data"}), 400

    sponsors = {
        s.id: s
        for s in Sponsor.query.filter(Sponsor.id.in_(ids)).all()
    }

    for item in data:
        s = sponsors.get(item.get("id"))
        if not s:
            continue
        try:
            s.orderz = int(item.get("orderz", s.orderz))
        except (TypeError, ValueError):
            continue

    db.session.commit()
    return jsonify({"message": "Order updated"}), 200
