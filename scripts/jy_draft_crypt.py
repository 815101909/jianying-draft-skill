#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪映 / CapCut 草稿「映映」加密 JSON 解密 / 加密工具（纯本地、可复现）

格式（见 references/jiangying-encrypted-json.md）:
  - 文件是 trimmed ASCII 文本
  - 载荷 = 标准 padded Base64，但被插入了 48 个额外 ASCII 字符
  - 这 48 字符 = key(32) || nonce(16)
  - AES-256-GCM，16 字节 nonce，无 AAD，16 字节 tag
  - 解码后布局 = ciphertext || tag（Go 标准 GCM sealed 布局）
  - 明文 = UTF-8 JSON

插入位置（每个位置放一个 4 字符块，按升序插入到逐步增长的 Base64 串中）:
  0, 7, 20, 33, 40, 47, 59, 66, 76, 89, 99, 127

用法:
  python jy_draft_crypt.py decrypt <in.json> [out.json]
  python jy_draft_crypt.py decrypt-dir <草稿目录> [输出目录]   # 整目录镜像解密
  python jy_draft_crypt.py encrypt <plain.json> [out.json]
  python jy_draft_crypt.py selftest
  python jy_draft_crypt.py scan <dir>            # 递归扫描加密草稿
"""

import base64
import json
import os
import re
import sys

POSITIONS = [0, 7, 20, 33, 40, 47, 59, 66, 76, 89, 99, 127]
CHUNK = 4
KEY_LEN = 32
NONCE_LEN = 16
TAG_LEN = 16

_B64_RE = re.compile(rb"^[A-Za-z0-9+/=\r\n]+$")


def looks_encrypted(raw: bytes) -> bool:
    """判断文件是否可能是映映加密格式（纯 base64 字符且不是 JSON）。"""
    s = raw.strip()
    if not s:
        return False
    if s[:1] in (b"{", b"["):
        return False
    if len(s) < POSITIONS[-1] + CHUNK:
        return False
    return bool(_B64_RE.match(s))


def decrypt_bytes(raw: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    work = list(raw.decode("ascii").strip())
    chunks = []
    for pos in reversed(POSITIONS):
        if pos + CHUNK > len(work):
            raise ValueError("payload too short at insertion position %d" % pos)
        chunks.append("".join(work[pos:pos + CHUNK]))
        del work[pos:pos + CHUNK]
    key_nonce = "".join(reversed(chunks))
    if len(key_nonce) != KEY_LEN + NONCE_LEN:
        raise ValueError("invalid key/nonce length: %d" % len(key_nonce))
    key = key_nonce[:KEY_LEN].encode("ascii")
    nonce = key_nonce[KEY_LEN:].encode("ascii")
    sealed = base64.b64decode("".join(work))
    plaintext = AESGCM(key).decrypt(nonce, sealed, None)
    try:
        plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("decrypted payload is not valid UTF-8") from exc
    json.loads(plaintext.decode("utf-8"))
    return plaintext


def encrypt_bytes(plaintext: bytes) -> bytes:
    """逆向 decrypt_bytes：把 key||nonce 切块按升序插回 Base64 串。

    注意：key||nonce 在原实现里是 48 个 ASCII 字符（其字节直接当 key/nonce 用），
    所以这里也从 base64 字母表里随机取 48 个 ASCII 字符，保证与真实格式同构。
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import secrets

    json.loads(plaintext.decode("utf-8"))  # 必须是合法 JSON
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    key_nonce = "".join(secrets.choice(alphabet) for _ in range(KEY_LEN + NONCE_LEN))
    key = key_nonce[:KEY_LEN].encode("ascii")
    nonce = key_nonce[KEY_LEN:].encode("ascii")
    sealed = AESGCM(key).encrypt(nonce, plaintext, None)  # ciphertext || tag
    b64 = base64.b64encode(sealed).decode("ascii")
    chunks = [key_nonce[i:i + CHUNK] for i in range(0, len(key_nonce), CHUNK)]
    if len(chunks) != len(POSITIONS):
        raise ValueError("chunk count mismatch")
    work = list(b64)
    for pos, chunk in zip(POSITIONS, chunks):  # 升序插入
        work[pos:pos] = chunk
    return "".join(work).encode("ascii")


def _load(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def _save(path: str, data: bytes) -> None:
    with open(path, "wb") as fh:
        fh.write(data)


def cmd_decrypt(args):
    src = args[0]
    dst = args[1] if len(args) > 1 else os.path.splitext(src)[0] + ".decrypted.json"
    raw = _load(src)
    if not looks_encrypted(raw):
        print("WARN: 该文件看起来不是映映加密格式（可能已是明文 JSON）", file=sys.stderr)
    pt = decrypt_bytes(raw)
    _save(dst, pt)
    print("OK  %s -> %s (%d bytes)" % (src, dst, len(pt)))


def cmd_encrypt(args):
    src = args[0]
    dst = args[1] if len(args) > 1 else os.path.splitext(src)[0] + ".encrypted.json"
    ct = encrypt_bytes(_load(src))
    _save(dst, ct)
    print("OK  %s -> %s (%d bytes)" % (src, dst, len(ct)))


def cmd_selftest(args):
    sample = json.dumps(
        {"id": "SELFTEST", "tracks": [], "n": 123, "pad": "x" * 64}, ensure_ascii=False
    ).encode("utf-8")
    enc = encrypt_bytes(sample)
    assert looks_encrypted(enc), "encrypted output should look encrypted"
    dec = decrypt_bytes(enc)
    assert json.loads(dec) == json.loads(sample), "round-trip mismatch"
    # 篡改一个字节必须导致认证失败
    bad = bytearray(enc)
    bad[10] = ord("A") if bad[10] != ord("A") else ord("B")
    try:
        decrypt_bytes(bytes(bad))
        raise AssertionError("tampered payload must fail GCM auth")
    except Exception as exc:
        if isinstance(exc, AssertionError):
            raise
    print("selftest OK: encrypt/decrypt round-trip + tamper detection passed")


def cmd_scan(args):
    root = args[0]
    hits = []
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            if not f.lower().endswith(".json"):
                continue
            p = os.path.join(dp, f)
            try:
                raw = _load(p)
            except OSError:
                continue
            if len(raw) < POSITIONS[-1] + CHUNK or not looks_encrypted(raw):
                continue
            try:
                pt = decrypt_bytes(raw)
                hits.append((len(raw), len(pt), p, True, pt[:48].decode("utf-8", "replace")))
            except Exception as exc:  # noqa: BLE001
                hits.append((len(raw), 0, p, False, str(exc)))
    hits.sort(reverse=True)
    for n, m, p, ok, info in hits:
        flag = "OK  " if ok else "FAIL"
        print("%s %10d -> %9d  %s\n        %s" % (flag, n, m, p, info))
    print("total encrypted-format files: %d" % len(hits))


def cmd_decrypt_dir(args):
    """把一个草稿目录里所有加密 JSON 解密到镜像目录，保留相对路径。"""
    src_root = args[0]
    dst_root = args[1] if len(args) > 1 else src_root.rstrip("\\/") + "_decrypted"
    n_ok = n_skip = n_fail = 0
    for dp, _dn, fn in os.walk(src_root):
        for f in fn:
            if not f.lower().endswith(".json"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, src_root)
            out = os.path.join(dst_root, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            try:
                raw = _load(p)
            except OSError:
                continue
            if not looks_encrypted(raw):
                _save(out, raw)  # 已是明文，原样镜像
                n_skip += 1
                continue
            try:
                _save(out, decrypt_bytes(raw))
                n_ok += 1
                print("OK   %s" % rel)
            except Exception as exc:  # noqa: BLE001
                n_fail += 1
                print("FAIL %s :: %s" % (rel, exc))
    print("done: decrypted=%d passthrough=%d failed=%d -> %s" % (n_ok, n_skip, n_fail, dst_root))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd, args = sys.argv[1], sys.argv[2:]
    table = {
        "decrypt": cmd_decrypt,
        "decrypt-dir": cmd_decrypt_dir,
        "encrypt": cmd_encrypt,
        "selftest": cmd_selftest,
        "scan": cmd_scan,
    }
    if cmd not in table:
        print(__doc__)
        return 2
    if cmd != "selftest" and not args:
        print(__doc__)
        return 2
    table[cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
