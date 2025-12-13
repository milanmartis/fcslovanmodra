# app/aws_utils.py
import os
import re
import mimetypes
from typing import Optional

import boto3
from botocore.config import Config as BotoConfig
from flask import current_app
from werkzeug.utils import secure_filename

_S3 = None
_S3_REGION = None

# voliteľné: validácia bucket name
_BUCKET_RE = re.compile(r'^[a-z0-9][a-z0-9.\-_]{1,61}[a-z0-9]$')


def _get_bucket() -> str:
    bucket = (current_app.config.get("AWS_S3_BUCKET") or "").strip()
    if not bucket:
        raise RuntimeError("AWS_S3_BUCKET is not set")
    # len základná kontrola (AWS má prísnejšie pravidlá, ale toto chytí najhoršie chyby)
    if not _BUCKET_RE.match(bucket):
        # nech to aspoň logicky vysvetlí problém
        raise RuntimeError(f"Invalid AWS_S3_BUCKET value: {bucket!r}")
    return bucket


def _get_credentials():
    ak = (current_app.config.get("AWS_ACCESS_KEY_ID") or "").strip()
    sk = (current_app.config.get("AWS_SECRET_ACCESS_KEY") or "").strip()
    if not ak or not sk:
        raise RuntimeError("AWS credentials missing: AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY")
    return ak, sk


def s3_extra_args(file) -> dict:
    """
    Nastaví správny ContentType podľa uploadovaného súboru
    + dlhú cache.
    """
    content_type = getattr(file, "mimetype", None)

    if not content_type or content_type == "application/octet-stream":
        content_type, _ = mimetypes.guess_type(getattr(file, "filename", ""))

    if not content_type:
        content_type = "application/octet-stream"

    return {
        "CacheControl": "public, max-age=31536000",
        "ContentType": content_type,
    }


def s3_client():
    """
    Vráti inicializovaný boto3 s3 client v reálnom regióne bucketu.
    Autodetect region bucketu + s3v4 podpis.
    """
    global _S3, _S3_REGION
    if _S3:
        return _S3

    bucket = _get_bucket()
    ak, sk = _get_credentials()

    # 1) probe bez regionu (AWS vráti LocationConstraint)
    probe = boto3.client("s3", aws_access_key_id=ak, aws_secret_access_key=sk)
    loc = probe.get_bucket_location(Bucket=bucket)
    _S3_REGION = loc.get("LocationConstraint") or "us-east-1"

    # 2) skutočný klient v regióne bucketu
    _S3 = boto3.client(
        "s3",
        region_name=_S3_REGION,
        aws_access_key_id=ak,
        aws_secret_access_key=sk,
        config=BotoConfig(signature_version="s3v4"),
    )
    return _S3


def s3_presign_get(key: str, expires_in: int = 3600) -> str:
    """Presigned URL na GET (čítanie)."""
    bucket = _get_bucket()
    return s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=int(expires_in),
    )


def s3_presign_put(
    key: str,
    expires_in: int = 3600,
    content_type: Optional[str] = None,
    acl: Optional[str] = None,
) -> str:
    """
    Presigned URL na PUT (upload).
    - content_type: ak chceš vynútiť ContentType pri uploadovaní.
    - acl: napr. "private" / "public-read" (väčšinou nechaj None).
    """
    bucket = _get_bucket()
    params = {"Bucket": bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    if acl:
        params["ACL"] = acl

    return s3_client().generate_presigned_url(
        "put_object",
        Params=params,
        ExpiresIn=int(expires_in),
    )


# spätná kompatibilita: tvoje produkty/posts už volajú s3_presign(...)
def s3_presign(key: str, expires_in: int = 3600) -> str:
    return s3_presign_get(key, expires_in=expires_in)


def sanitize_filename(filename: str) -> str:
    """
    Bezpečný názov súboru (bez diakritiky/medzier/čudných znakov).
    """
    return secure_filename(filename or "")


# ---------- Key helpers ----------

def make_post_key(post_id: int, filename: str) -> str:
    return f"posts/{int(post_id)}/gallery/{filename}"


def make_product_key(product_id: int, filename: str) -> str:
    return f"products/{int(product_id)}/gallery/{filename}"


def make_sponsor_key(filename: str) -> str:
    # môžeš mať aj podsložky: sponsors/logo.png
    # filename tu očakávam už "secure" (ale pre istotu ho preženieme)
    clean = sanitize_filename(filename)
    return f"sponsors/{clean}"


def make_sponsor_key_by_id(sponsor_id: int, filename: str) -> str:
    """
    Ak chceš mať sponsor obrázky per-sponsor:
    sponsors/<id>/<filename>
    """
    clean = sanitize_filename(filename)
    return f"sponsors/{int(sponsor_id)}/{clean}"
