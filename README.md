# ISBN Validation API

A simple Flask API I built for Algebraic Coding Theory . It validates and processes
ISBN-10 and ISBN-13 numbers using their official check digit rules — no extra libraries,
just Flask.

---

## What It Does

- Computes the check digit of an ISBN-10
- Validates an ISBN-10 (including the special **X** case)
- Converts an ISBN-10 to ISBN-13
- Validates an ISBN-13

---

## How to Run It

Make sure Flask is installed, activate your virtual environment, then run:

```powershell
python ISBN-Api.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debugger is active!
```

That means it's live and ready to use.

---

## Endpoints
this are the endpoints used as requisted

| Endpoint | What it does |
|----------|-------------|
| `POST /isbn10/check-digit` | Give it 9 digits, it returns the check digit |
| `POST /isbn10/validate` | Checks if a full ISBN-10 is valid or not |
| `POST /isbn10/to-isbn13` | Converts a valid ISBN-10 to ISBN-13 |
| `POST /isbn13/validate` | Checks if a full ISBN-13 is valid or not |

All endpoints accept JSON input like `{ "isbn": "your_number_here" }`.

---

## Tested and Working

I tested all the endpoints using PowerShell.The code was runned in vs code using a virtual enviroment to test the output as required. Here's a sample from one of the tests:

**Check Digit Test — input: `061826030` (first 9 digits)**
```
check_digit  full_isbn10  input
-----------  -----------  -----
7            0618260307   061826030
```
The API correctly computed **7** as the check digit and returned the full ISBN-10 as `0618260307`.

All other endpoints (validate, convert, ISBN-13) also returned the correct results.
The special case where the check digit is **X** (value = 10) was also handled correctly.

---

## How the ISBN-10 Rule Works

Each digit is multiplied by its position weight (10 down to 1), all products are added
up, and the total must be divisible by 11 to be valid.

Example for `0618260307`:
```
0×10 + 6×9 + 1×8 + 8×7 + 2×6 + 6×5 + 0×4 + 3×3 + 0×2 + 7×1 = 176
176 ÷ 11 = 16, remainder 0 → VALID ✅
```

---

## Author
- **Name:** [Derrick Gitonga Maina]
- **Course:**  Mathematics and Computer Science
_ **Unit** Algebraic Coding Theory
- **Date:** 2026

