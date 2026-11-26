# 加密草稿 JSON

Use this reference when a Jianying draft file is not plain JSON and appears to have been written by 映映小助手. This format carries a per-file AES key and nonce inside the encoded text; it does not use a fixed application key.

## Format

- Treat the file as trimmed ASCII text.
- The payload is standard padded Base64 with 48 extra ASCII characters inserted into it.
- The 48 characters are `key || nonce`:
  - first 32 bytes: AES-256 key;
  - next 16 bytes: GCM nonce.
- AES mode: AES-256-GCM with a **16-byte nonce**, no AAD, and a 16-byte authentication tag.
- The decoded Base64 bytes use Go's standard GCM sealed layout: `ciphertext || tag`.
- Decrypted bytes are UTF-8 JSON.

The insertion positions are:

```text
0, 7, 20, 33, 40, 47, 59, 66, 76, 89, 99, 127
```

Each position holds one 4-character chunk. Encryption inserts chunks in ascending position order into the progressively growing Base64 string.

## Decryption

1. Try parsing the file as ordinary JSON first. Only try this format after plain JSON parsing fails.
2. Convert the trimmed input to a mutable character array.
3. Iterate the insertion positions in reverse order.
4. At each position, remove exactly four characters and save that chunk.
5. Reverse the collected chunk list, then concatenate it. Do not merely concatenate chunks as they are removed.
6. Split the recovered 48 ASCII bytes into a 32-byte key and 16-byte nonce.
7. Concatenate the remaining characters and standard-Base64 decode them.
8. AES-256-GCM decrypt the decoded `ciphertext || tag` with the recovered key, nonce, and empty AAD.
9. Require successful GCM authentication, valid UTF-8, and valid JSON before accepting the result.

Pseudocode:

```text
positions = [0, 7, 20, 33, 40, 47, 59, 66, 76, 89, 99, 127]
work = chars(trim(input))
chunks = []

for pos in reverse(positions):
    require pos + 4 <= len(work)
    chunks.append(remove work[pos : pos + 4])

key_nonce = concat(reverse(chunks))
require len_ascii_bytes(key_nonce) == 48
key = key_nonce[0:32]
nonce = key_nonce[32:48]
ciphertext_and_tag = base64_standard_decode(concat(work))
plaintext = aes_256_gcm_decrypt(key, nonce, ciphertext_and_tag, aad=nil)
return parse_utf8_json(plaintext)
```

## Implementation Notes

### Bundled tools (Windows)

Inspect encrypted or plain drafts without changing the input:

```powershell
py "<skill>/scripts/inspect_draft.py" "C:/drafts/example/draft_content.json" --pretty
```

The inspector uses the same decoder as the style extractor. To obtain a plaintext copy directly, build `scripts/decrypt_yingying_json.go` and send its UTF-8 stdout to a new file. PowerShell redirection encoding varies by version; Python can preserve the output bytes:

```powershell
go build -o "$env:TEMP/jianying-decrypt.exe" "<skill>/scripts/decrypt_yingying_json.go"
# Only run the next command after go build succeeds. Choose a new destination.
py -c "import pathlib,subprocess,sys; data=subprocess.run(sys.argv[1:3],check=True,capture_output=True).stdout; pathlib.Path(sys.argv[3]).open('xb').write(data)" "$env:TEMP/jianying-decrypt.exe" "C:/drafts/example/draft_content.json" "C:/drafts/example/draft_content.decrypted.json"
```

The destination uses exclusive creation (`xb`), so an existing file is not overwritten. Python is needed for inspection; Go is additionally needed for this encrypted format. A failed authentication or unknown format must remain an error. Do not generalize the historical verification below to every encrypted file produced by Jianying.

- Go: use `cipher.NewGCMWithNonceSize(block, 16)` and `Open(nil, nonce, sealed, nil)`.
- Rust `aes-gcm`: the default `Aes256Gcm` alias assumes a 12-byte nonce. Define `AesGcm<aes::Aes256, U16>` instead.
- .NET's built-in `AesGcm` commonly rejects a 16-byte nonce. Use a provider that supports generic GCM nonce sizes or implement this component in Rust/Go.
- Do not write the plaintext over the source unless explicitly requested. Prefer in-memory decoding or a copied template.
- On Base64, length, UTF-8, JSON, or authentication failure, stop and report an unsupported/changed/corrupt format. Never return unauthenticated plaintext.

## Verification Marker

This algorithm was verified against a real encrypted Jianying backup. Successful decryption produced draft ID `61E43025BA98303D32C1B8D32DE5456F` and valid JSON. Treat that ID only as a historical test marker, not as a key or format constant.
