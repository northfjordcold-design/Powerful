# 🔐 Encryption Playground

A beginner-friendly, interactive Streamlit app for learning how encryption and encoding
work — with live results, step-by-step visualisations, and plain-English explanations
built right into the UI.

> **Educational use only.** This app is designed to teach concepts. For real-world
> applications, always use battle-tested libraries and established protocols rather than
> building cryptography from scratch.

---

## Table of Contents

1. [What This App Does](#what-this-app-does)
2. [Project Structure](#project-structure)
3. [Requirements & Installation](#requirements--installation)
4. [Running the App](#running-the-app)
5. [Deploying to Streamlit Cloud](#deploying-to-streamlit-cloud)
6. [How the Code is Organised](#how-the-code-is-organised)
7. [Cipher Deep Dives](#cipher-deep-dives)
   - [Caesar Cipher](#-caesar-cipher)
   - [Vigenère Cipher](#-vigenère-cipher)
   - [AES-256](#-aes-256)
   - [Base64 Encoding](#-base64-encoding)
8. [Streamlit Concepts Used](#streamlit-concepts-used)
9. [Known Limitations](#known-limitations)
10. [Ideas for Extending the App](#ideas-for-extending-the-app)

---

## What This App Does

The Encryption Playground lets you type any message and run it through four different
cryptographic methods, watching exactly what happens at each step. Rather than treating
encryption as a black box, every mode shows its working — which letter moved where, which
keyword shift was applied, what the raw bytes look like after AES processes them, and so on.

The four modes are:

| Mode | Difficulty | Library needed |
|------|-----------|----------------|
| 🟢 Caesar Cipher | Beginner | None (pure Python) |
| 🟡 Vigenère Cipher | Intermediate | None (pure Python) |
| 🔴 AES-256 | Advanced | `cryptography` |
| ⚪ Base64 Encoding | Concept only | None (stdlib) |

---

## Project Structure

```
your-repo/
├── encryption_playground.py   # The entire Streamlit app (single file)
├── requirements.txt           # Python dependencies for Streamlit Cloud
└── README.md                  # This file
```

Everything lives in one file. There are no sub-modules, no config files, and no database.
All state is held in Streamlit's session state during the browser session and is lost on
page refresh.

---

## Requirements & Installation

**Python version:** 3.8 or higher.

**Dependencies:**

```
streamlit
cryptography
```

These are also listed in `requirements.txt`, which Streamlit Cloud reads automatically
on deployment.

To install locally:

```bash
pip install streamlit cryptography
```

The `cryptography` package is only imported when you navigate to the AES-256 mode (lazy
import — explained below). The rest of the app works without it.

---

## Running the App

```bash
streamlit run encryption_playground.py
```

Streamlit will open a browser tab at `http://localhost:8501`. Use the **sidebar** on the
left to switch between encryption methods.

---

## Deploying to Streamlit Cloud

1. Push both `encryption_playground.py` and `requirements.txt` to a GitHub repository
   (they must be in the same directory).
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account.
3. Select the repository, branch, and `encryption_playground.py` as the entry point.
4. Click **Deploy**. Streamlit Cloud will read `requirements.txt` and install dependencies
   automatically before starting the app.

> **Troubleshooting:** If you see a `ModuleNotFoundError` on Streamlit Cloud, the most
> common cause is a missing or incorrectly placed `requirements.txt`. It must sit in the
> same directory as the `.py` file, not in a subdirectory.

---

## How the Code is Organised

The file is divided into five logical sections, in order:

### 1. Imports

```python
import streamlit as st
import base64
import os
```

Only the standard library and Streamlit are imported at the top level. The `cryptography`
library is **not** imported here — it is imported lazily inside the `aes_encrypt` and
`aes_decrypt` functions. This is intentional: a top-level import that fails (e.g. because
the package is mid-install on Streamlit Cloud) crashes the entire app before any UI
renders. Lazy imports confine the failure to the AES section only.

### 2. Page Config & Custom CSS

```python
st.set_page_config(...)
st.markdown("<style>...</style>", unsafe_allow_html=True)
```

`st.set_page_config` must always be the very first Streamlit call in the script, before
any other `st.*` function. It sets the browser tab title, the favicon emoji, and switches
the layout to `"wide"` so the columns have more room.

The CSS block injects a dark terminal aesthetic — black background (`#0d0d0d`), glowing
green headings and result boxes (`#00ff88`), and monospace fonts throughout. Streamlit
allows raw HTML/CSS via `st.markdown(..., unsafe_allow_html=True)`. Three custom CSS
classes are defined here and reused across all modes:

- `.explainer` — the green-left-bordered info box shown at the top of each mode.
- `.result-box` — the dark green bordered box where encrypted/decrypted output is shown.
- `.step` — individual rows in the step-by-step breakdown expanders.

### 3. Cipher Functions

Four pure Python functions implement the cryptographic logic. They are defined before any
UI code so that the UI sections can call them freely.

### 4. App Header & Sidebar

```python
st.title(...)
with st.sidebar:
    method = st.selectbox(...)
```

The sidebar contains a single `st.selectbox` that returns the name of the selected cipher
as a string. This string (`method`) is then used as the condition in the `if/elif` chain
that follows. Every time the user changes the dropdown, Streamlit re-runs the entire script
from top to bottom, and a different `elif` branch executes.

### 5. Cipher UI Sections (if/elif chain)

Each of the four modes is an `elif` block. Only one block runs per script execution. Each
block follows the same pattern:

1. Show the `.explainer` div (concept + security notes).
2. Render inputs (text fields, sliders, radio buttons).
3. Call the corresponding cipher function.
4. Display the result in a `.result-box`.
5. Show a visualisation (alphabet diagram, keyword alignment, hex output, byte breakdown).
6. Offer an expander with step-by-step details.

---

## Cipher Deep Dives

### 🟢 Caesar Cipher

**Function:** `caesar_cipher(text, shift, decrypt=False)`

The Caesar cipher replaces every letter with the letter a fixed number of positions ahead
in the alphabet. With `shift=3`, A becomes D, B becomes E, Z wraps around to C, and so on.
Decryption simply applies a negative shift.

**The maths:**

```
new_position = (original_position + shift) % 26
```

The modulo operator (`% 26`) is what makes the alphabet circular — position 25 (Z) plus
1 becomes position 0 (A), not position 26 (which doesn't exist).

**Case preservation:** The code checks `char.isupper()` and sets `base` to either
`ord('A')` (65) or `ord('a')` (97). Subtracting `base` from the character's ASCII code
normalises it to a 0–25 range, applies the shift, then adds `base` back. This means
uppercase and lowercase letters are shifted independently and their case is preserved.

**Non-letter characters** (spaces, punctuation, digits) are passed through unchanged.

**Return value:** A tuple of `(result_string, steps_list)`. The steps list contains one
human-readable string per letter, showing its original position, the shift applied, its
new position, and the resulting character. The UI caps display at 30 steps to avoid
overwhelming the page.

**UI extras:** Below the result, a two-column alphabet diagram shows the plain alphabet
aligned against the shifted alphabet, making the substitution table visible at a glance.

**Security note:** There are only 25 possible non-zero shifts for a 26-letter alphabet.
An attacker can try all 25 in under a second, or use letter frequency analysis (E is the
most common letter in English — whichever ciphertext letter appears most often is probably E).

---

### 🟡 Vigenère Cipher

**Function:** `vigenere_cipher(text, key, decrypt=False)`

The Vigenère cipher extends Caesar by using a keyword instead of a single shift number.
Each letter of the keyword contributes a different shift value. The keyword repeats for
as long as the plaintext continues.

**Example with key `"SECRET"`:**

```
Plaintext:   A  T  T  A  C  K
Key letters: S  E  C  R  E  T
Shifts:      18 4  2  17 4  19
Ciphertext:  S  X  V  R  G  D
```

The shift for each letter is derived from the key letter's position in the alphabet:
`ord(key_letter) - ord('A')`. So S (position 18) contributes shift 18, E (position 4)
contributes shift 4, and so on.

**Key cycling:** The variable `key_index` increments only when an alphabetic character is
processed. This ensures that spaces and punctuation in the message do not consume a key
letter, keeping the key aligned with the actual letters.

**Decryption** negates the shift: `shift = -shift`.

**Return value:** Same structure as Caesar — `(result_string, steps_list)`, where each
step shows the plaintext letter, which key letter was used, the resulting shift, and the
ciphertext letter.

**UI extras:** A keyword alignment diagram shows the message letters on one row and the
repeating keyword letters directly beneath them, making the relationship between key and
message concrete.

**Security note:** The Vigenère cipher was considered unbreakable for about 300 years
until Charles Babbage (and independently Friedrich Kasiski) showed that repeated key
patterns leave statistical fingerprints in the ciphertext. The **Kasiski test** finds
repeated sequences in the ciphertext, uses their spacing to guess the key length, and then
treats each key-length-spaced group of letters as a simple Caesar cipher — each of which
is trivially breakable by frequency analysis.

---

### 🔴 AES-256

**Functions:** `aes_encrypt(plaintext, key_hex)` and `aes_decrypt(ciphertext_hex, key_hex, iv_hex)`

AES (Advanced Encryption Standard) is the symmetric encryption algorithm used by
governments, banks, messaging apps, and essentially all modern secure communication.
"Symmetric" means the same key is used to both encrypt and decrypt.

This app uses **AES-256-CBC**:

- **256** — the key is 256 bits long (32 bytes, expressed as 64 hexadecimal characters).
- **CBC** — Cipher Block Chaining mode, where each 16-byte block of plaintext is XORed
  with the previous ciphertext block before being encrypted. This means identical plaintext
  blocks produce different ciphertext blocks, hiding repetition in the data.

**The three components you need:**

| Component | Size | Secret? | Purpose |
|-----------|------|---------|---------|
| Key | 32 bytes (64 hex chars) | ✅ Yes | Controls the encryption; never share it |
| IV (Initialization Vector) | 16 bytes (32 hex chars) | ❌ No | Randomises the first block; must be stored alongside the ciphertext |
| Ciphertext | Variable | N/A | The encrypted output |

**Encryption flow:**

1. Convert the hex key string to raw bytes with `bytes.fromhex(key_hex)`.
2. Generate a fresh random IV with `os.urandom(16)`. A new IV is generated on every
   encryption call — this is critical. Reusing an IV with the same key leaks information
   about the relationship between two messages.
3. Apply **PKCS7 padding** to the plaintext. AES works on fixed 16-byte blocks. If the
   plaintext length is not a multiple of 16, padding bytes are appended. PKCS7 padding
   fills the remaining bytes with the number of bytes added (e.g. if 5 bytes of padding
   are needed, five `\x05` bytes are appended). This is removed during decryption.
4. Create a `Cipher` object from the `cryptography` library using the key and IV, run the
   encryptor, and collect the output bytes.
5. Return the ciphertext as a hex string (easier to display and copy than raw binary).

**Decryption flow:** The exact reverse — convert hex inputs back to bytes, create a
`Cipher` in decrypt mode, run the decryptor, and strip the PKCS7 padding.

**Lazy import pattern:**

```python
def aes_encrypt(plaintext, key_hex):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding
    ...
```

The `cryptography` imports are placed inside the function body rather than at the top of
the file. Python caches module imports, so this does not cause repeated loading — the first
call imports and caches, subsequent calls return the cached module instantly. The benefit
is that the app starts and renders all other modes even if `cryptography` is not yet
installed.

**UI:** The AES section uses `st.tabs` to split the Encrypt and Decrypt workflows onto
separate tabs, keeping the interface uncluttered. The 🎲 **Random key** button calls
`os.urandom(32).hex()` and stores the result in `st.session_state["aes_key"]`. Session
state persists the key across re-runs so it does not disappear when the user clicks
Encrypt.

**Security note:** Brute-forcing a 256-bit key is computationally infeasible —
2²⁵⁶ possible keys means even a computer testing a trillion keys per second would take
far longer than the age of the universe. The real-world risks with AES are: weak key
generation, IV reuse, improper key storage, and side-channel attacks — not brute force.

---

### ⚪ Base64 Encoding

Base64 is **not encryption**. It is an encoding scheme that converts arbitrary binary data
into a string of 64 printable ASCII characters (A–Z, a–z, 0–9, `+`, `/`). Anyone who sees
a Base64 string can decode it instantly — there is no key, no secret, no confidentiality.

**Why it exists:** Many text-based protocols (email, HTTP headers, HTML attributes, JSON)
cannot safely carry raw binary bytes. Base64 provides a way to represent binary data
(images, files, encrypted blobs) as plain text that travels safely through these channels.

**How it works:** Every 3 bytes of input (24 bits) are split into four 6-bit groups. Each
6-bit group maps to one of the 64 characters in the Base64 alphabet. If the input length
is not divisible by 3, `=` padding characters are appended to make the output length a
multiple of 4. This is why Base64 output is always about 33% larger than the input.

**In the app:** For short inputs (9 characters or fewer), the UI shows a byte-level
breakdown displaying each character's ASCII code and its 8-bit binary representation,
then explains how those bits are grouped into 6-bit chunks.

**Common places you see Base64:**

- JWT tokens (the three `.`-separated parts of a JSON Web Token are Base64-encoded)
- `data:image/png;base64,...` URIs embedded in HTML/CSS
- Email attachments (MIME encoding)
- API request/response bodies carrying binary payloads
- Encoded credentials in HTTP Basic Authentication headers

---

## Streamlit Concepts Used

| Concept | Where used | What it does |
|---------|-----------|--------------|
| `st.set_page_config` | Top of file | Sets tab title, icon, layout width |
| `st.markdown(..., unsafe_allow_html=True)` | CSS injection, explainer boxes, result boxes | Renders raw HTML/CSS inside the app |
| `st.sidebar` | Method selector | Persistent panel on the left for navigation |
| `st.selectbox` | Sidebar | Dropdown that returns the selected string |
| `st.columns` | Input layout | Splits the page into side-by-side columns |
| `st.text_input` | Message inputs | Single-line text entry |
| `st.text_area` | AES plaintext | Multi-line text entry |
| `st.number_input` | Caesar shift | Numeric stepper with min/max bounds |
| `st.radio` | Encrypt/Decrypt toggle | Horizontal button group |
| `st.tabs` | AES section | Tabbed panels for Encrypt vs Decrypt |
| `st.expander` | Step-by-step details | Collapsible section to hide verbose output |
| `st.button` | Encrypt/Decrypt triggers | Executes logic on click |
| `st.code` | Alphabet diagrams, key display | Monospace code block |
| `st.session_state` | AES random key | Persists values across re-runs |
| `st.divider` | Visual separator | Horizontal rule |
| `st.caption` | Footer | Small grey helper text |
| `st.warning` / `st.error` | Validation feedback | Coloured alert banners |

**Streamlit's execution model:** Every time a user interacts with any widget, Streamlit
re-runs the entire Python script from top to bottom. There is no event loop or callback
system like in traditional GUI frameworks. This means all logic is written linearly — you
read widget values, compute results, and render output in one pass. `st.session_state` is
the mechanism for carrying values across re-runs (e.g. persisting the randomly generated
AES key so it does not regenerate every time the Encrypt button is clicked).

---

## Known Limitations

- **AES key persistence:** The randomly generated AES key is stored in `st.session_state`,
  which lives for the duration of the browser session. Refreshing the page clears it. In a
  real application you would write keys to secure storage, not session state.
- **No file input:** The app only encrypts/decrypts typed text. It does not support
  uploading files.
- **AES output is not portable:** The ciphertext hex and IV hex are shown on screen but
  not offered as a download. For a long message, copying hex manually is impractical.
- **No authentication on AES:** The app uses CBC mode without a Message Authentication
  Code (MAC). In production, you should use an authenticated mode like AES-GCM to detect
  ciphertext tampering.
- **Vigenère key sanitisation:** The key input strips non-alphabetic characters silently
  and falls back to `"KEY"` if the result is empty. This could confuse users who paste a
  key containing numbers.

---

## Ideas for Extending the App

- **Caesar brute-force tab:** Add a button that tries all 25 shifts and shows the one that
  produces the most English-looking output (score by dictionary word matches or letter
  frequency). This teaches why short keyspaces are insecure.
- **Frequency analysis chart:** Plot the letter frequency of ciphertext vs. standard
  English. Vigenère disrupts the pattern; Caesar only shifts it.
- **File upload for AES:** Use `st.file_uploader` to accept any file, encrypt its bytes,
  and offer the result as a download via `st.download_button`.
- **AES-GCM mode:** Swap CBC for GCM (Galois/Counter Mode) to demonstrate authenticated
  encryption and show what happens when the ciphertext is tampered with.
- **RSA key pair generator:** Add a tab that generates an RSA public/private key pair,
  encrypts a short message with the public key, and decrypts with the private key —
  illustrating asymmetric encryption.
- **Password-based key derivation:** Instead of asking for a raw hex key, let the user
  type a password and derive the AES key using PBKDF2 or Argon2, demonstrating why
  passwords are not directly usable as cryptographic keys.
- **Kasiski test tool:** Given a Vigenère ciphertext, find repeated trigrams and their
  spacing to guess the key length automatically.
  
