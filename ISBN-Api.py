from flask import Flask, request, jsonify

app = Flask(__name__)


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def clean_isbn10(isbn):
    """Strip hyphens/spaces and upper-case any X."""
    return isbn.replace("-", "").replace(" ", "").upper()


def clean_isbn13(isbn):
    """Strip hyphens/spaces from an ISBN-13 candidate."""
    return isbn.replace("-", "").replace(" ", "")


def compute_isbn10_check_digit(first9):
    """
    Given the first 9 digits of an ISBN-10 (as a string),
    compute and return the check digit (0-9 or 'X').
    Returns None if the input is not exactly 9 numeric digits.
    """
    if len(first9) != 9 or not first9.isdigit():
        return None

    total = sum((10 - i) * int(first9[i]) for i in range(9))
    remainder = total % 11
    check = (11 - remainder) % 11
    return "X" if check == 10 else str(check)


def validate_isbn10(isbn):
    """
    Validate a full 10-character ISBN-10.
    Returns (is_valid: bool, error_msg: str | None).
    """
    if len(isbn) != 10:
        return False, "ISBN-10 must be exactly 10 characters."

    # First 9 must be digits; last may be digit or X
    if not isbn[:9].isdigit():
        return False, "First 9 characters of ISBN-10 must be digits."

    if isbn[9] not in "0123456789X":
        return False, "Last character of ISBN-10 must be a digit or 'X'."

    last = 10 if isbn[9] == "X" else int(isbn[9])
    total = sum((10 - i) * int(isbn[i]) for i in range(9)) + last

    if total % 11 == 0:
        return True, None
    return False, "Check digit does not satisfy the ISBN-10 validation rule."


def isbn10_to_isbn13(isbn10):
    """
    Convert a validated ISBN-10 to ISBN-13.
    Prepend '978', drop the ISBN-10 check digit, compute new check digit.
    Returns the 13-digit ISBN-13 string.
    """
    body = "978" + isbn10[:9]          # 12 digits without check digit

    # ISBN-13 check digit: alternating weights 1 and 3
    total = sum(
        int(body[i]) * (1 if i % 2 == 0 else 3)
        for i in range(12)
    )
    check = (10 - (total % 10)) % 10
    return body + str(check)


def validate_isbn13(isbn):
    """
    Validate a full 13-digit ISBN-13.
    Returns (is_valid: bool, error_msg: str | None).
    """
    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN-13 must be exactly 13 numeric digits."

    total = sum(
        int(isbn[i]) * (1 if i % 2 == 0 else 3)
        for i in range(13)
    )

    if total % 10 == 0:
        return True, None
    return False, "Check digit does not satisfy the ISBN-13 validation rule."


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.route("/isbn10/check-digit", methods=["POST"])
def isbn10_check_digit():
    """
    Compute the check digit for the first 9 digits of an ISBN-10.

    Request JSON:  { "isbn": "061826030" }   (9 digits)
    Response JSON: {
        "input": "061826030",
        "check_digit": "7",
        "full_isbn10": "0618260307"
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = str(data["isbn"]).strip()
    first9 = raw.replace("-", "").replace(" ", "")

    check = compute_isbn10_check_digit(first9)
    if check is None:
        return jsonify({
            "error": "Input must be exactly 9 numeric digits (the first 9 of an ISBN-10).",
            "input": raw
        }), 400

    return jsonify({
        "input": raw,
        "check_digit": check,
        "full_isbn10": first9 + check
    })


@app.route("/isbn10/validate", methods=["POST"])
def isbn10_validate():
    """
    Validate a full ISBN-10.

    Request JSON:  { "isbn": "0618260307" }
    Response JSON: {
        "input": "0618260307",
        "check_digit": "7",
        "valid": true
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = str(data["isbn"]).strip()
    isbn = clean_isbn10(raw)

    is_valid, error = validate_isbn10(isbn)

    if not is_valid and error and "10 characters" in error:
        return jsonify({"error": error, "input": raw}), 400

    return jsonify({
        "input": raw,
        "check_digit": isbn[-1] if len(isbn) == 10 else None,
        "valid": is_valid,
        **({"reason": error} if error else {})
    })


@app.route("/isbn10/to-isbn13", methods=["POST"])
def isbn10_to_isbn13_endpoint():
    """
    Convert a valid ISBN-10 to ISBN-13.

    Request JSON:  { "isbn": "0618260307" }
    Response JSON: {
        "input": "0618260307",
        "valid": true,
        "isbn13": "9780618260300"
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = str(data["isbn"]).strip()
    isbn = clean_isbn10(raw)

    is_valid, error = validate_isbn10(isbn)
    if not is_valid:
        return jsonify({
            "error": "Cannot convert an invalid ISBN-10.",
            "input": raw,
            "valid": False,
            "reason": error
        }), 400

    isbn13 = isbn10_to_isbn13(isbn)
    return jsonify({
        "input": raw,
        "valid": True,
        "isbn13": isbn13
    })


@app.route("/isbn13/validate", methods=["POST"])
def isbn13_validate():
    """
    Validate a full ISBN-13.

    Request JSON:  { "isbn": "9780618260300" }
    Response JSON: {
        "input": "9780618260300",
        "valid": true
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = str(data["isbn"]).strip()
    isbn = clean_isbn13(raw)

    is_valid, error = validate_isbn13(isbn)

    if not is_valid and "13 numeric" in (error or ""):
        return jsonify({"error": error, "input": raw}), 400

    return jsonify({
        "input": raw,
        "valid": is_valid,
        **({"reason": error} if error else {})
    })


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)