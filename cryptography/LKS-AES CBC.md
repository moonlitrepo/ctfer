# AES CBC LKS

## Deskripsi
Hanya admin yang mendapatkan burger bangor.

## Source Code

```python
import json
import re
from os import urandom

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

BLOCK_SIZE = 16
KEY = urandom(BLOCK_SIZE)
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{1,25}$")
MENU = (
    "\n"
    "1. Create session\n"
    "2. Login with session\n"
    "3. Exit\n"
    "> "
)

def load_flag() -> str:
    with open("flag.txt", "r", encoding="utf-8") as flag_file:
        return flag_file.read().strip()

def sanitize_username(username: str) -> str:
    if not USERNAME_RE.fullmatch(username):
        raise ValueError("Username must be 1 to 25 characters and use only letters, digits, or underscores")
    return username

def build_profile(username: str) -> bytes:
    username = sanitize_username(username)
    profile = {
        "username": username,
        "isAdmin": 0,
    }
    return json.dumps(profile, separators=(",", ":")).encode()

def issue_cookie(username: str) -> str:
    iv = urandom(BLOCK_SIZE)
    plaintext = build_profile(username)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, BLOCK_SIZE))
    return (iv + ciphertext).hex()

def decrypt_cookie(token_hex: str) -> bytes:
    raw = bytes.fromhex(token_hex)
    if len(raw) < BLOCK_SIZE * 2 or len(raw) % BLOCK_SIZE != 0:
        raise ValueError("Invalid cookie format")

    iv = raw[:BLOCK_SIZE]
    ciphertext = raw[BLOCK_SIZE:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), BLOCK_SIZE)

def check_admin(token_hex: str, flag: str) -> tuple[bool, str]:
    try:
        plaintext = decrypt_cookie(token_hex)
        profile = json.loads(plaintext.decode("latin-1"))
    except Exception:
        return False, "Invalid session"

    if profile.get("isAdmin") == 1:
        return True, f"Welcome back, admin. {flag}"
    return False, "Hello, user"

def main() -> None:
    flag = load_flag()

    while True:
        print(MENU, end="", flush=True)
        try:
            choice = input().strip()
        except EOFError:
            break

        if choice == "1":
            print("Username: ", end="", flush=True)
            try:
                username = input().strip()
                cookie = issue_cookie(username)
            except ValueError as exc:
                print(f"Error: {exc}", flush=True)
                continue
            except EOFError:
                break

            print(f"Session: {cookie}", flush=True)

        elif choice == "2":
            print("Session token: ", end="", flush=True)
            try:
                cookie = input().strip()
            except EOFError:
                break
            ok, message = check_admin(cookie, flag)
            print(message, flush=True)
            if ok:
                break

        elif choice == "3":
            print("Goodbye", flush=True)
            break

        else:
            print("Unknown option", flush=True)

if __name__ == "__main__":
    main()
```

## Analisis

Di challenge ini kita diberikan pembuat cookie sederhana, di mana cookie dienkripsi dengan AES-CBC. Username yang kita masukkan akan dimasukkan ke dalam JSON:

```json
{"username": "username", "isAdmin": 0}
```

lalu diubah menjadi string dan dienkripsi.

Selain itu, ada sistem pengecekan admin — kita dianggap admin jika `"isAdmin": 1`. Jadi, kita bisa memanipulasi ciphertext dari server untuk mengubah string `"0"` menjadi `"1"` agar mendapatkan flag.

## Solusi

Karena tidak ada autentikasi tambahan (seperti MAC/HMAC) sebelum ciphertext didekripsi, kita bisa langsung melakukan **XOR** pada ciphertext:

- XOR-kan byte target ciphertext dengan `"0"` dan `"1"`.
- Karena sifat XOR, `"0"` dari ciphertext dan `"0"` yang kita masukkan akan saling menghilangkan `((A ^ B) ^ A = B)`, sehingga byte tersebut akhirnya berubah menjadi `"1"`.

Sebelum melakukan XOR, kita harus tahu **posisi pasti** dari karakter `"0"` (nilai `isAdmin`) di dalam ciphertext.

### Mencari Posisi Byte Target

Plaintext percobaan untuk username `"a"`:

```json
{"username":"a","isAdmin":0}
```

Panjangnya 28 byte. Setelah dienkripsi:
```
fa6f3b8f64f002f891cbadd82a2d8afb85b279714fe58ee87531aaf841ef7b445ec951742bad5dd6c56bd07794d4d9cc
```

Panjangnya 48 byte (termasuk IV).

Kita perlu memastikan bagian `{"username":"...","isAdmin":0}` berada tepat di **blok terakhir**, supaya saat proses dekripsi, JSON yang dikirim untuk dicek tidak rusak dan tetap bisa dibaca server.

Untuk itu, kita buat username menjadi `"a" * 19`, sehingga JSON menjadi:

```json
{"username":"aaaaaaaaaaaaaaaaaaa","isAdmin":0}
```

Pembagian per blok (16 byte per blok):
- **Blok 0**: `{"username":"aaa`
- **Blok 1**: `aaaaaaaaaaaaaaaa`
- **Blok 2**: `","isAdmin":0}`

Sekarang karakter `"0"` berada di **index ke-12** pada blok 2. Untuk mendapatkan posisi absolutnya:
```
32 (total byte blok 0 & 1) + 12 = 44
```

Jadi karakter `"0"` berada di **index ke-44** pada ciphertext (dengan IV di depan). Tinggal kita flip byte ini agar berubah menjadi `"1"`, sehingga server menganggap kita admin dan memberikan flag.

### Byte Flipping Attack

Teknik ini disebut **byte flipping attack**.

Karena index 44 berada di **blok ciphertext ke-2**, memodifikasi byte pada blok ciphertext ke-1 (blok sebelumnya) akan memengaruhi hasil dekripsi blok ke-2 pada posisi yang sama (karena mode CBC melakukan XOR antara hasil dekripsi blok ciphertext saat ini dengan blok ciphertext sebelumnya).

Saat kita XOR-kan byte pada index 44 blok ciphertext ke-1 dengan `"0" ^ "1"`, maka:

- Blok plaintext ke-1 (blok "tumbal") akan berubah menjadi byte acak/sampah — ini tidak masalah karena blok ini bukan bagian JSON yang kita perhatikan.
- Blok plaintext ke-2 pada index 44 (yang bernilai `"0"`) akan ter-XOR dengan `"0" ^ "1"`, sehingga hasilnya:

"0" ^ ("0" ^ "1") = "1"


Karena blok ke-1 menjadi rusak (byte sampah), ada kemungkinan hasil dekripsi blok tersebut membuat keseluruhan JSON tidak valid (`Invalid session`). Karena itu, cookie hasil flip perlu dicoba berulang kali sampai diterima oleh server.

## Solver

```python
from pwn import *

io = process(["python3", "chall.py"])

def get_cookie(username):
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"Username: ", username.encode())
    hasil = io.recvline().decode().strip()
    print(hasil)
    return bytes.fromhex(hasil.split(": ", 1)[1])

def check_cookie(cookie_new):
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"Session token: ", cookie_new.hex().encode())
    return io.recvline()

for percobaan in range(1, 200):
    cookie_enc = bytearray(get_cookie("a" * 19))

    cookie_enc[44] ^= ord("0") ^ ord("1")
    respon = check_cookie(bytes(cookie_enc))
    if b"Welcome back, admin." in respon:
        print(respon.decode())
        break
```
