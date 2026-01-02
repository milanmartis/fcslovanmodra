import os
import uuid
from io import BytesIO

from PIL import Image, ImageOps, features
from werkzeug.utils import secure_filename


def _encode_under_limit(img: Image.Image, *, fmt: str, target_bytes: int,
                        start_q: int, min_q: int, step: int, **save_kwargs) -> BytesIO:
    """
    Ukladá obrázok opakovane s klesajúcou kvalitou, kým sa nezmestí do target_bytes
    alebo nedosiahne min_q.
    """
    q = max(1, min(int(start_q), 95))
    min_q = max(1, min(int(min_q), 95))
    step = max(1, int(step))

    last_buf = None
    while True:
        buf = BytesIO()
        img.save(buf, format=fmt, quality=q, **save_kwargs)
        size = buf.tell()
        last_buf = buf
        if size <= target_bytes or q <= min_q:
            buf.seek(0)
            return buf
        q -= step


def _process_image_to_bytes(file_storage, *, max_size, max_kb,
                            prefer_webp=True,
                            webp_start_q=78, webp_min_q=40,
                            jpg_start_q=75, jpg_min_q=40):
    """
    Vráti (bytes_io, content_type, ext) pre obrázky.
    Ak to nie je obrázok -> vráti (None, None, None).
    """
    try:
        # načítaj od začiatku
        try:
            file_storage.stream.seek(0)
        except Exception:
            pass

        img = Image.open(file_storage.stream)
        img = ImageOps.exif_transpose(img)

        # resize
        img.thumbnail(max_size)

        target_bytes = int(max_kb) * 1024

        # --- WebP, ak je podporované ---
        if prefer_webp and features.check("webp"):
            # WebP vyžaduje RGB pre lossy použitie (bez alpha)
            if img.mode in ("RGBA", "P"):
                img2 = img.convert("RGBA")
                bg = Image.new("RGBA", img2.size, (255, 255, 255, 255))
                img2 = Image.alpha_composite(bg, img2).convert("RGB")
            else:
                img2 = img.convert("RGB")

            buf = _encode_under_limit(
                img2,
                fmt="WEBP",
                target_bytes=target_bytes,
                start_q=webp_start_q,
                min_q=webp_min_q,
                step=7,
                method=6,
                optimize=True,
            )
            return buf, "image/webp", ".webp"

        # --- JPEG fallback (vždy dostupné) ---
        # JPEG len RGB
        if img.mode in ("RGBA", "P"):
            img2 = img.convert("RGBA")
            bg = Image.new("RGBA", img2.size, (255, 255, 255, 255))
            img2 = Image.alpha_composite(bg, img2).convert("RGB")
        else:
            img2 = img.convert("RGB")

        buf = _encode_under_limit(
            img2,
            fmt="JPEG",
            target_bytes=target_bytes,
            start_q=jpg_start_q,
            min_q=jpg_min_q,
            step=7,
            optimize=True,
            progressive=True,
        )
        return buf, "image/jpeg", ".jpg"

    except Exception:
        # nie je to obrázok alebo sa nedá spracovať
        try:
            file_storage.stream.seek(0)
        except Exception:
            pass
        return None, None, None


def upload_post_file_to_s3(
    *,
    file,
    post_id: int,
    bucket_name: str,
    make_gallery_key,
    s3_client,
    s3_extra_args,
    max_size=(1200, 1200),
    max_kb=300,
):
    """
    - Ak je to obrázok: resize + kompresia do max_kb (default 300KB) a upload bytes do S3
      (preferuje WebP, inak JPEG fallback).
    - Ak nie je obrázok: upload originál.

    Returns: (new_filename, s3_key)
    """
    original = secure_filename(file.filename)
    base, ext = os.path.splitext(original)
    ext = (ext or "").lower()

    # 1) Skús spracovať ako obrázok
    buf, content_type, out_ext = _process_image_to_bytes(
        file,
        max_size=max_size,
        max_kb=max_kb,
        prefer_webp=True,
    )

    if buf is not None:
        new_filename = f"{uuid.uuid4().hex}_{base}{out_ext}"
        s3_key = make_gallery_key(post_id, new_filename)

        extra = s3_extra_args(file) or {}
        extra["ContentType"] = content_type
        extra.setdefault("CacheControl", "public, max-age=31536000, immutable")

        s3_client().upload_fileobj(
            buf,
            bucket_name,
            s3_key,
            ExtraArgs=extra
        )
        return new_filename, s3_key

    # 2) Nie je obrázok -> originál
    new_filename = f"{uuid.uuid4().hex}_{base}{ext}"
    s3_key = make_gallery_key(post_id, new_filename)

    try:
        file.stream.seek(0)
    except Exception:
        pass

    s3_client().upload_fileobj(
        file,
        bucket_name,
        s3_key,
        ExtraArgs=s3_extra_args(file),
    )
    return new_filename, s3_key
