# cryptohack-password as keys

CTF	= Cryptohack
Nama Chall  =  Passwords as Keys
Kategori  =  Crypto

Deskripsi Chall
It is essential that keys in symmetric-key algorithms are random bytes, instead of passwords or other predictable data. The random bytes should be generated using a cryptographically-secure pseudorandom number generator (CSPRNG). If the keys are predictable in any way, then the security level of the cipher is reduced and it may be possible for an attacker who gets access to the ciphertext to decrypt it.

Just because a key looks like it is formed of random bytes, does not mean that it necessarily is. In this case the key has been derived from a simple password using a hashing function, which makes the ciphertext crackable.

For this challenge you may script your HTTP requests to the endpoints, or alternatively attack the ciphertext offline. Good luck!

Link yang diberikan = https://aes.cryptohack.org/passwords_as_keys

Analisis
Ketika link kita click maka kita di arahkan ke sebuah halaman web yang di mana di situ kita dikasih sebuah source code dari kode python yang mengenkripsi flag 

SC=
from Crypto.Cipher import AES
import hashlib
import random

```Python
# /usr/share/dict/words from
# https://gist.githubusercontent.com/wchargin/8927565/raw/d9783627c731268fb2935a731a618aa8e95cf465/words
with open("/usr/share/dict/words") as f:
    words = [w.strip() for w in f.readlines()]
keyword = random.choice(words)

KEY = hashlib.md5(keyword.encode()).digest()
FLAG = ?


@chal.route('/passwords_as_keys/decrypt/<ciphertext>/<password_hash>/')
def decrypt(ciphertext, password_hash):
    ciphertext = bytes.fromhex(ciphertext)
    key = bytes.fromhex(password_hash)

    cipher = AES.new(key, AES.MODE_ECB)
    try:
        decrypted = cipher.decrypt(ciphertext)
    except ValueError as e:
        return {"error": str(e)}

    return {"plaintext": decrypted.hex()}


@chal.route('/passwords_as_keys/encrypt_flag/')
def encrypt_flag():
    cipher = AES.new(KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(FLAG.encode())

    return {"ciphertext": encrypted.hex()}
```
secara singkat source code ini mengenkripsi flag menggunakan aes mode ECB,di sana pembuat chall membuat kunci dari kata random yang ada di file words.txt,lalu kata acak dari words.txt tadi diubah jadi hash md 5 lalu flag di enkripsi pakai AES ECB.kita juga dikasih file words.txt dengan kita menulis menulis https://gist.githubusercontent.com/wchargin/8927565/raw/d9783627c731268fb2935a731a618aa8e95cf465/words di kolom url browser

# Solusi
Karena kita bisa mengakses file yang isi nya ada kata untuk key dari aes yang mengenkripsi flag jadi kita bisa mencoba satu persatu kata untuk di jadikan kunci dan mencocokan hasilnya  dengan hasil deskripsi dari ciphertext 


<img width="491" height="430" alt="image" src="https://github.com/user-attachments/assets/5db1158f-d711-47c6-97f4-66e1957db331" />








