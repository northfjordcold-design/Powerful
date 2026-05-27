"""
🔐 Encryption Playground
A beginner-friendly Streamlit app to learn encryption interactively.

HOW TO RUN:
  1. pip install streamlit cryptography
  2. streamlit run encryption_playground.py

WHAT'S INSIDE:
  - Caesar Cipher   (ancient substitution cipher)
  - Vigenère Cipher (poly-alphabetic cipher)
  - AES Encryption  (modern symmetric encryption)
  - Base64 Encoding (encoding, not encryption – learn the difference!)
"""

import streamlit as st
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be the very first st. call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🔐 Encryption Playground",
    page_icon="🔐",
    layout="wide",
)

# ─────────────────────────────────────────────
# CUSTOM CSS  – dark terminal / cyber aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark background */
  .stApp { background-color: #0d0d0d; color: #e0e0e0; }

  /* Glowing green headings */
  h1, h2, h3 { color: #00ff88 !important; font-family: 'Courier New', monospace; }

  /* Info / explainer boxes */
  .explainer {
    background: #111;
    border-left: 4px solid #00ff88;
    border-radius: 6px;
    padding: 14px 18px;
    font-family: 'Courier New', monospace;
    font-size: 0.88rem;
    color: #aaa;
    margin-bottom: 1rem;
  }

  /* Result output box */
  .result-box {
    background: #0a1a0a;
    border: 1px solid #00ff88;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 1rem;
    color: #00ff88;
    word-break: break-all;
    margin-top: 0.5rem;
  }

  /* Step-by-step visualization */
  .step {
    background: #111;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 4px 0;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
  }

  .arrow { color: #00ff88; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# CIPHER IMPLEMENTATIONS
# ══════════════════════════════════════════════

def caesar_cipher(text: str, shift: int, decrypt: bool = False) -> tuple[str, list[str]]:
    """
    Caesar Cipher: shift each letter by a fixed number of positions.
    Returns the result AND a list of steps showing how each letter moved.
    """
    if decrypt:
        shift = -shift  # decrypting = shifting backwards

    result = []
    steps = []

    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            original_pos = ord(char) - base          # position 0–25
            new_pos = (original_pos + shift) % 26    # wrap around with modulo
            new_char = chr(base + new_pos)
            result.append(new_char)
            steps.append(
                f"'{char}' (pos {original_pos:>2}) "
                f"→ shift {shift:+d} "
                f"→ pos {new_pos:>2} "
                f"→ '{new_char}'"
            )
        else:
            result.append(char)     # spaces / punctuation unchanged
            if char != " ":
                steps.append(f"'{char}' → unchanged (not a letter)")

    return "".join(result), steps


def vigenere_cipher(text: str, key: str, decrypt: bool = False) -> tuple[str, list[str]]:
    """
    Vigenère Cipher: like Caesar but the shift changes with each letter,
    driven by a repeating keyword.
    """
    key = key.upper()
    key_index = 0
    result = []
    steps = []

    for char in text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')  # key letter → shift amount
            if decrypt:
                shift = -shift
            base = ord('A') if char.isupper() else ord('a')
            new_char = chr((ord(char) - base + shift) % 26 + base)
            result.append(new_char)
            key_letter = key[key_index % len(key)]
            steps.append(
                f"'{char}' + key[{key_index % len(key)}]='{key_letter}' "
                f"(shift {shift:+d}) → '{new_char}'"
            )
            key_index += 1
        else:
            result.append(char)

    return "".join(result), steps


def aes_encrypt(plaintext: str, key_hex: str) -> tuple[str, str, str]:
    """
    AES-256-CBC encryption.
    Returns: (ciphertext_hex, iv_hex, status_message)
    AES needs:
      - A 32-byte (256-bit) key
      - A random 16-byte IV (Initialization Vector) per encryption
      - Padding to fill incomplete blocks
    """
    try:
        key_bytes = bytes.fromhex(key_hex)
        if len(key_bytes) != 32:
            return "", "", "❌ Key must be exactly 64 hex characters (32 bytes / 256 bits)."

        iv = os.urandom(16)   # fresh random IV every time – crucial for security!

        # PKCS7 padding: pad plaintext to a multiple of 16 bytes
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext.encode()) + padder.finalize()

        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        return ciphertext.hex(), iv.hex(), "✅ Encrypted successfully!"
    except Exception as e:
        return "", "", f"❌ Error: {e}"


def aes_decrypt(ciphertext_hex: str, key_hex: str, iv_hex: str) -> tuple[str, str]:
    """
    AES-256-CBC decryption.
    You MUST supply the same key AND the same IV used during encryption.
    """
    try:
        key_bytes = bytes.fromhex(key_hex)
        iv_bytes = bytes.fromhex(iv_hex)
        ct_bytes = bytes.fromhex(ciphertext_hex)

        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plain = decryptor.update(ct_bytes) + decryptor.finalize()

        # Remove PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plain) + unpadder.finalize()

        return plaintext.decode(), "✅ Decrypted successfully!"
    except Exception as e:
        return "", f"❌ Error: {e}"


# ══════════════════════════════════════════════
# APP HEADER
# ══════════════════════════════════════════════

st.title("🔐 Encryption Playground")
st.markdown(
    "Learn how encryption works by doing it. "
    "Pick a method, type your message, and watch every step."
)
st.divider()


# ══════════════════════════════════════════════
# SIDEBAR – choose cipher
# ══════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ Settings")
    method = st.selectbox(
        "Choose an encryption method",
        ["Caesar Cipher", "Vigenère Cipher", "AES-256", "Base64 Encoding"],
    )

    st.markdown("---")
    st.markdown("""
    **Difficulty guide**
    - 🟢 Caesar – easiest
    - 🟡 Vigenère – medium
    - 🔴 AES-256 – industry standard
    - ⚪ Base64 – not encryption!
    """)


# ══════════════════════════════════════════════
# ① CAESAR CIPHER
# ══════════════════════════════════════════════

if method == "Caesar Cipher":
    st.header("① Caesar Cipher")

    st.markdown("""
    <div class="explainer">
    📜 <b>How it works:</b> Every letter is shifted forward (or backward) by a fixed number
    of positions in the alphabet. Julius Caesar reportedly used shift=3.
    <br><br>
    🔓 <b>Security:</b> Extremely weak — only 25 possible keys. Breakable in seconds.
    <br><br>
    💡 <b>Key concept:</b> Modular arithmetic (% 26) wraps Z back around to A.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        text_in = st.text_input("Your message", value="Hello World")
    with col2:
        shift = st.number_input("Shift amount", min_value=1, max_value=25, value=3)

    mode = st.radio("Mode", ["Encrypt", "Decrypt"], horizontal=True)
    decrypt = mode == "Decrypt"

    if text_in:
        result, steps = caesar_cipher(text_in, shift, decrypt)

        st.markdown(f"**Result:**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

        with st.expander("🔍 Show letter-by-letter steps"):
            for s in steps[:30]:    # cap at 30 so it doesn't overflow
                st.markdown(f'<div class="step">{s}</div>', unsafe_allow_html=True)
            if len(steps) > 30:
                st.caption(f"… and {len(steps) - 30} more letters")

        # Alphabet shift visualisation
        st.markdown("**Alphabet shift diagram** (shift = {})".format(shift))
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        shifted = alphabet[shift:] + alphabet[:shift]
        col_a, col_b = st.columns(2)
        with col_a:
            st.code("Plain:  " + " ".join(list(alphabet)))
        with col_b:
            st.code("Cipher: " + " ".join(list(shifted)))


# ══════════════════════════════════════════════
# ② VIGENÈRE CIPHER
# ══════════════════════════════════════════════

elif method == "Vigenère Cipher":
    st.header("② Vigenère Cipher")

    st.markdown("""
    <div class="explainer">
    📜 <b>How it works:</b> Like Caesar, but instead of one fixed shift, you use a keyword.
    Each letter of the keyword sets the shift for the corresponding letter in your message.
    The keyword repeats as needed.
    <br><br>
    🔓 <b>Security:</b> Much stronger than Caesar, but still breakable with frequency analysis
    (Kasiski test). Was considered "unbreakable" for 300 years!
    <br><br>
    💡 <b>Key concept:</b> The shift cycles through the keyword — "KEY" means shifts of 10, 4, 24.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        text_in = st.text_input("Your message", value="Attack at dawn")
    with col2:
        key = st.text_input("Keyword (letters only)", value="SECRET")
        key = ''.join(c for c in key if c.isalpha()) or "KEY"  # sanitise

    mode = st.radio("Mode", ["Encrypt", "Decrypt"], horizontal=True)

    if text_in:
        result, steps = vigenere_cipher(text_in, key, mode == "Decrypt")

        st.markdown("**Result:**")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

        # Show the keyword mapped onto the message
        st.markdown("**Keyword alignment:**")
        letters_only = [c for c in text_in.upper() if c.isalpha()]
        key_repeated = [key.upper()[i % len(key)] for i in range(len(letters_only))]
        st.code("Message: " + " ".join(letters_only))
        st.code("Key:     " + " ".join(key_repeated))

        with st.expander("🔍 Show step-by-step"):
            for s in steps[:20]:
                st.markdown(f'<div class="step">{s}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# ③ AES-256
# ══════════════════════════════════════════════

elif method == "AES-256":
    st.header("③ AES-256 Encryption")

    st.markdown("""
    <div class="explainer">
    🏭 <b>How it works:</b> AES (Advanced Encryption Standard) is the gold standard for
    symmetric encryption. It operates on 16-byte "blocks" through 14 rounds of substitution,
    permutation, and mixing. This app uses CBC mode with a random IV each time.
    <br><br>
    🔑 <b>Key:</b> 256 bits = 32 bytes = 64 hex characters. Keep it secret!
    <br><br>
    🎲 <b>IV (Initialization Vector):</b> Random data mixed in before encryption so that
    encrypting the same message twice gives different ciphertext. You need to store/share
    the IV alongside the ciphertext to decrypt later — it's not a secret.
    <br><br>
    🔒 <b>Security:</b> Brute-forcing a 256-bit key would take longer than the age of the universe.
    </div>
    """, unsafe_allow_html=True)

    tab_enc, tab_dec = st.tabs(["🔒 Encrypt", "🔓 Decrypt"])

    with tab_enc:
        plaintext = st.text_area("Message to encrypt", value="Top secret message!")

        st.markdown("**256-bit Key** (64 hex characters)")
        col1, col2 = st.columns([4, 1])
        with col1:
            key_hex = st.text_input(
                "Key (hex)", 
                value="0" * 64,
                label_visibility="collapsed"
            )
        with col2:
            if st.button("🎲 Random key"):
                st.session_state["aes_key"] = os.urandom(32).hex()

        # Use session state key if generated
        if "aes_key" in st.session_state:
            key_hex = st.session_state["aes_key"]
            st.code(f"Generated key: {key_hex}")

        if st.button("🔒 Encrypt", type="primary"):
            ct_hex, iv_hex, status = aes_encrypt(plaintext, key_hex)
            st.markdown(status)
            if ct_hex:
                st.markdown("**Ciphertext (hex):**")
                st.markdown(f'<div class="result-box">{ct_hex}</div>', unsafe_allow_html=True)
                st.markdown("**IV (save this to decrypt later!):**")
                st.code(iv_hex)

                st.markdown("""
                <div class="explainer">
                💾 To decrypt, you need <b>all three</b>: the ciphertext, the key, and the IV.
                Lose any one of them → data is gone forever.
                </div>
                """, unsafe_allow_html=True)

    with tab_dec:
        ct_input = st.text_input("Ciphertext (hex)")
        key_input = st.text_input("Key (hex, 64 chars)")
        iv_input = st.text_input("IV (hex, 32 chars)")

        if st.button("🔓 Decrypt", type="primary"):
            if ct_input and key_input and iv_input:
                plaintext_out, status = aes_decrypt(ct_input, key_input, iv_input)
                st.markdown(status)
                if plaintext_out:
                    st.markdown("**Decrypted message:**")
                    st.markdown(f'<div class="result-box">{plaintext_out}</div>', unsafe_allow_html=True)
            else:
                st.warning("Please fill in all three fields.")


# ══════════════════════════════════════════════
# ④ BASE64
# ══════════════════════════════════════════════

elif method == "Base64 Encoding":
    st.header("④ Base64 Encoding")

    st.markdown("""
    <div class="explainer">
    ⚠️ <b>NOT encryption!</b> Base64 is <em>encoding</em>, not encryption.
    It converts binary data into printable ASCII text using 64 characters (A-Z, a-z, 0-9, +, /).
    Anyone can decode it instantly — there is no key.
    <br><br>
    📦 <b>Use cases:</b> Sending binary data (images, files) over text-based protocols
    like email (MIME), embedding images in HTML/CSS, JWT tokens, API payloads.
    <br><br>
    💡 <b>Rule of thumb:</b> Every 3 bytes of input → 4 characters of Base64 output (~33% larger).
    </div>
    """, unsafe_allow_html=True)

    text_in = st.text_area("Input text", value="Hello, this is NOT encrypted!")
    mode = st.radio("Mode", ["Encode", "Decode"], horizontal=True)

    if text_in:
        try:
            if mode == "Encode":
                encoded = base64.b64encode(text_in.encode()).decode()
                st.markdown("**Base64 encoded:**")
                st.markdown(f'<div class="result-box">{encoded}</div>', unsafe_allow_html=True)

                # Show byte-level breakdown for short inputs
                if len(text_in) <= 9:
                    st.markdown("**How each character maps:**")
                    for char in text_in:
                        bits = format(ord(char), '08b')
                        st.markdown(
                            f'<div class="step">'
                            f"'{char}' → ASCII {ord(char)} → binary <b>{bits}</b>"
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    st.caption("Base64 groups these bits into 6-bit chunks, then maps each to one of 64 characters.")
            else:
                decoded = base64.b64decode(text_in.encode()).decode()
                st.markdown("**Decoded text:**")
                st.markdown(f'<div class="result-box">{decoded}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Could not process input: {e}")

    st.markdown("---")
    st.markdown("**🔑 Key takeaway:**")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        **Encoding** (Base64)
        - No key needed
        - Anyone can reverse it
        - Purpose: data portability
        """)
    with cols[1]:
        st.markdown("""
        **Encryption** (AES, etc.)
        - Requires a secret key
        - Useless without the key
        - Purpose: confidentiality
        """)


# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════

st.divider()
st.caption(
    "🎓 Educational use only. "
    "For real-world secrets, use battle-tested libraries like `cryptography` or `PyNaCl` — "
    "never roll your own crypto in production."
)
