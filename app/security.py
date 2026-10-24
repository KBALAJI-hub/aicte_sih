import base64
import hashlib
import hmac
import io
import qrcode

# Secret key used for signing tamper-evident student hashes
HMAC_SECRET_KEY = b"aicte-apaar-tamper-proof-secret-2026"


def generate_student_hash(
    apaar_id: str,
    institution_id: int,
    program_id: int,
    student_id: str,
    dob: str
) -> str:
    """
    Computes a cryptographic HMAC-SHA256 signature across core student fields.
    Guarantees record integrity against unauthorized database modifications.
    """
    payload = f"{apaar_id}|{institution_id}|{program_id}|{student_id}|{dob}"
    signature = hmac.new(
        HMAC_SECRET_KEY,
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_student_hash(
    apaar_id: str,
    institution_id: int,
    program_id: int,
    student_id: str,
    dob: str,
    expected_hash: str
) -> bool:
    """
    Validates if the stored record hash matches recomputed HMAC signature.
    """
    actual_hash = generate_student_hash(
        apaar_id, institution_id, program_id, student_id, dob
    )
    return hmac.compare_digest(actual_hash, expected_hash or "")


def generate_qr_code_base64(data: str) -> str:
    """
    Generates a QR code image encoded as a Base64 data URI string.
    Can be directly rendered in Jinja2 templates via `<img src="{{ qr_code }}" />`.
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=6,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"
