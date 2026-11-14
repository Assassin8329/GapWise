"""
Pure Python implementation of AES-256 in Galois/Counter Mode (GCM).
Conforms to NIST SP 800-38D.
Zero external dependencies.
"""

import struct
import hmac

# S-Box
SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5e, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

def _sub_word(word: int) -> int:
    return (SBOX[(word >> 24) & 0xff] << 24) | \
           (SBOX[(word >> 16) & 0xff] << 16) | \
           (SBOX[(word >> 8) & 0xff] << 8) | \
           SBOX[word & 0xff]

def _rot_word(word: int) -> int:
    return ((word << 8) & 0xffffffff) | (word >> 24)

def _key_expansion_256(key: bytes):
    w = [0] * 60
    for i in range(8):
        w[i] = (key[4*i] << 24) | (key[4*i+1] << 16) | (key[4*i+2] << 8) | key[4*i+3]
    for i in range(8, 60):
        temp = w[i-1]
        if i % 8 == 0:
            temp = _sub_word(_rot_word(temp)) ^ (RCON[i // 8] << 24)
        elif i % 8 == 4:
            temp = _sub_word(temp)
        w[i] = w[i-8] ^ temp
    return w

def _xtimes(b: int) -> int:
    return ((b << 1) ^ 0x1b) & 0xff if (b & 0x80) else (b << 1) & 0xff

def _aes_block_encrypt(block: bytes, round_keys) -> bytes:
    state = list(block)
    # Add initial round key
    for i in range(4):
        rk = round_keys[i]
        state[4*i] ^= (rk >> 24) & 0xff
        state[4*i+1] ^= (rk >> 16) & 0xff
        state[4*i+2] ^= (rk >> 8) & 0xff
        state[4*i+3] ^= rk & 0xff

    for round_num in range(1, 14):
        # SubBytes
        for i in range(16):
            state[i] = SBOX[state[i]]
        # ShiftRows
        s = state
        state = [
            s[0], s[5], s[10], s[15],
            s[4], s[9], s[14], s[3],
            s[8], s[13], s[2], s[7],
            s[12], s[1], s[6], s[11]
        ]
        # MixColumns
        new_state = [0] * 16
        for c in range(4):
            c4 = c * 4
            a0, a1, a2, a3 = state[c4], state[c4+1], state[c4+2], state[c4+3]
            new_state[c4]   = _xtimes(a0) ^ _xtimes(a1) ^ a1 ^ a2 ^ a3
            new_state[c4+1] = a0 ^ _xtimes(a1) ^ _xtimes(a2) ^ a2 ^ a3
            new_state[c4+2] = a0 ^ a1 ^ _xtimes(a2) ^ _xtimes(a3) ^ a3
            new_state[c4+3] = _xtimes(a0) ^ a0 ^ a1 ^ a2 ^ _xtimes(a3)
        state = new_state
        # AddRoundKey
        rk_idx = round_num * 4
        for i in range(4):
            rk = round_keys[rk_idx + i]
            state[4*i] ^= (rk >> 24) & 0xff
            state[4*i+1] ^= (rk >> 16) & 0xff
            state[4*i+2] ^= (rk >> 8) & 0xff
            state[4*i+3] ^= rk & 0xff

    # Round 14: SubBytes, ShiftRows, AddRoundKey (No MixColumns)
    for i in range(16):
        state[i] = SBOX[state[i]]
    s = state
    state = [
        s[0], s[5], s[10], s[15],
        s[4], s[9], s[14], s[3],
        s[8], s[13], s[2], s[7],
        s[12], s[1], s[6], s[11]
    ]
    rk_idx = 14 * 4
    for i in range(4):
        rk = round_keys[rk_idx + i]
        state[4*i] ^= (rk >> 24) & 0xff
        state[4*i+1] ^= (rk >> 16) & 0xff
        state[4*i+2] ^= (rk >> 8) & 0xff
        state[4*i+3] ^= rk & 0xff

    return bytes(state)

# Galois Field GF(2^128) arithmetic for GHASH
# Polynomial: x^128 + x^7 + x^2 + x + 1 => R = 0xe1 << 120
R_POLY = 0xe1000000000000000000000000000000

def _gf_mult(x: int, y: int) -> int:
    z = 0
    v = x
    for i in range(128):
        if (y >> (127 - i)) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ R_POLY
        else:
            v >>= 1
    return z

def _ghash(h_int: int, aad: bytes, cipher: bytes) -> bytes:
    def pad16(data: bytes) -> bytes:
        pad_len = (16 - (len(data) % 16)) % 16
        return data + b'\x00' * pad_len

    data = pad16(aad) + pad16(cipher) + struct.pack('>QQ', len(aad) * 8, len(cipher) * 8)
    y = 0
    for i in range(0, len(data), 16):
        block_int = int.from_bytes(data[i:i+16], 'big')
        y = _gf_mult(y ^ block_int, h_int)
    return y.to_bytes(16, 'big')

def aes_256_gcm_encrypt(key: bytes, nonce: bytes, plaintext: bytes, associated_data: bytes = b'') -> bytes:
    """
    Encrypts plaintext using AES-256-GCM.
    Returns: nonce (12 bytes) + ciphertext + tag (16 bytes).
    """
    if len(key) != 32:
        raise ValueError("AES-256 requires a 32-byte key.")
    if len(nonce) != 12:
        raise ValueError("GCM requires a 12-byte (96-bit) nonce.")

    round_keys = _key_expansion_256(key)
    # Compute H = AES_K(0^128)
    h_bytes = _aes_block_encrypt(b'\x00' * 16, round_keys)
    h_int = int.from_bytes(h_bytes, 'big')

    # Initial counter block J0 = Nonce || 0x00000001
    j0 = nonce + b'\x00\x00\x00\x01'
    ctr = 1

    # Encrypt plaintext with CTR
    ciphertext = bytearray(len(plaintext))
    for offset in range(0, len(plaintext), 16):
        ctr += 1
        cb = nonce + struct.pack('>I', ctr)
        keystream_block = _aes_block_encrypt(cb, round_keys)
        chunk = plaintext[offset:offset+16]
        for i in range(len(chunk)):
            ciphertext[offset + i] = chunk[i] ^ keystream_block[i]

    # Compute GHASH and Tag
    s_tag = _ghash(h_int, associated_data, bytes(ciphertext))
    j0_enc = _aes_block_encrypt(j0, round_keys)
    tag = bytes(a ^ b for a, b in zip(s_tag, j0_enc))

    return nonce + bytes(ciphertext) + tag

def aes_256_gcm_decrypt(key: bytes, encrypted_payload: bytes, associated_data: bytes = b'') -> bytes:
    """
    Decrypts payload (nonce + ciphertext + tag) using AES-256-GCM.
    Raises ValueError if tag check fails or data is corrupted/tampered.
    """
    if len(key) != 32:
        raise ValueError("AES-256 requires a 32-byte key.")
    if len(encrypted_payload) < 28: # 12 nonce + 0 data + 16 tag
        raise ValueError("Payload too short for AES-GCM.")

    nonce = encrypted_payload[:12]
    tag = encrypted_payload[-16:]
    ciphertext = encrypted_payload[12:-16]

    round_keys = _key_expansion_256(key)
    h_bytes = _aes_block_encrypt(b'\x00' * 16, round_keys)
    h_int = int.from_bytes(h_bytes, 'big')

    j0 = nonce + b'\x00\x00\x00\x01'
    s_tag = _ghash(h_int, associated_data, ciphertext)
    j0_enc = _aes_block_encrypt(j0, round_keys)
    computed_tag = bytes(a ^ b for a, b in zip(s_tag, j0_enc))

    if not hmac.compare_digest(tag, computed_tag):
        raise ValueError("AES-256-GCM authentication failed: tag mismatch or payload tampered!")

    # Decrypt CTR
    ctr = 1
    plaintext = bytearray(len(ciphertext))
    for offset in range(0, len(ciphertext), 16):
        ctr += 1
        cb = nonce + struct.pack('>I', ctr)
        keystream_block = _aes_block_encrypt(cb, round_keys)
        chunk = ciphertext[offset:offset+16]
        for i in range(len(chunk)):
            plaintext[offset + i] = chunk[i] ^ keystream_block[i]

    return bytes(plaintext)
