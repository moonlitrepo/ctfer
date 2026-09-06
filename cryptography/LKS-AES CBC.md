# AES CBC LKS

# Deskripsi
Hanya admin yang mendapatkan burger bangor


# Analisis

Source code =
```Python
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

di chall ini kita di berikan pembuat cookie sederhana dimana cookie di enkripsi dengan aes cbc.username yang kita masukan akan di masukan ke json {"username":”username”,"isAdmin": 0} lalu di buat string dan dienkrispsi.setelah itu ada juga system pengecekkan admin,kita di katakan admin jika json "isAdmin": 1,jadi kita bisa memanipulasi chipher text dari server untuk kita ubah string “0” jadi 1 supaya mendapat flag.
Solusi

Dikarena kan sebelum chipher text di deskripsi tidak ada autentifikasi tambahan,jadi kita bisa langsung mengxorkan chipher text “0” dengan “0” dan dengan “1”,nanti “0” dari chipher text dan “0” dari kita akan saling menghilangkan di karena kan sifat dari xor,lalu nanti “0” yang ada di chipher text akan berubah jadi “1”  ((A^B) ^ A = B).Jadi sebelum kita mengoxkan “0” kita harus tau,posisi pasti dari “0”.sebelum di enkripsi plain text percobaan kita Adalah {"username":"a","isAdmin":0} yang panjang nya Adalah 28 dan jika sudah di enkripsi akan menghasilkan fa6f3b8f64f002f891cbadd82a2d8afb85b279714fe58ee87531aaf841ef7b445ec951742bad5dd6c56bd07794d4d9cc yang panjangnya 48.disini kita harus membuat {"username":"a","isAdmin":0} ada di blok terakhir supaya saat di deskripsi plain text json yang kita kirim untuk di check apakah admin bernilai 1 tidak rusak dan terbaca oleh server.jadi kita buat username nya jadi “a” * 19 nanti akan menjadi string json akan menjadi {"username":"aaaaaaaaaaaaaaaaaaa","isAdmin":0}.blok plaintext ke 0 akan terisi {"username":"aaa,blok 1 akan terisi aaaaaaaaaaaaaaaa dan blok 2 akan terisi ","isAdmin":0}.jadi sekarang 0 ada di index ke 12,cara mencari posisi pasti nya 
32(total bytes di blok 1 & 2) + 12 = 44
jadi “0” ada di index ke 44,setelah tau posisinya tinggal kita flip “0” supaya berubah jadi “1” agar kita di anggap admin dan di kasih flag.teknik ini Namanya Adalah byte flipping attack.
karena di index 44(blok 2 dari chipher text dan blok 1 plain text)kita rubah dengan meng xor kan nya dengan “0” dan “1” maka blok 1 plain text akan jadi acak,untuk di jadikan tumbal saat proses dekripsi 
supaya saat proses deskripsi hasil dari chipher text blok ke 2 index 44 bisa di xor dengan chipher text blok ke 1 index ke 44 yang kita sudah ubah nilai nya jadi “0” ^ “1”,sehingga nanti index 44 dari 
plain text yang nilai nya “0” akan di xorkan dengan “0” ^ “1” (( “0” ^ (“0” ^ “1”)) nanti hasilnya akan menjadi “1”.Karena blok yang ke 1 plaintext kita tumbal kan maka hasilnya bisa berkemungkinan besar
akan berubah jadi byte sampah yang membuat saat kita cek admin akan invalid,jadi kita tinggal memasukan cookie yang sudah kita flip secara berulang sampai cookie kita di acc server
SOLVER
```Python
from pwn import *
io = process(["python3","chall.py"])
def get_cookie(username):
    io.sendlineafter(b"> ",b"1")
    io.sendlineafter(b"Username: ",username.encode())
    hasil = io.recvline().decode().strip()
    print(hasil)
    return bytes.fromhex(hasil.split(": ",1)[1])
    
def check_cookie(cookie_new):
    io.sendlineafter(b"> ",b"2")
    io.sendlineafter(b"Session token: ",cookie_new.hex().encode())
    
    return io.recvline()

for percobaan in range(1,200):
    cookie_enc = bytearray(get_cookie("a" * 19))

    cookie_enc[44] ^= ord("0") ^ ord("1")
    respon = check_cookie(bytes(cookie_enc))
    if b"Welcome back, admin." in respon:
        print(respon.decode())
        break
```


