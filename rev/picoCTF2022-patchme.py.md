# picoCTF2022-patchme.py

# overview
<img width="434" height="261" alt="image" src="https://github.com/user-attachments/assets/01e9a3e2-0aa1-4ce6-8bf7-c5ddfaf932e9" />

challenge reverse engineering yang super sederhana. cukup buka source code dan dapatkan password. oiya. pastikan file flag.txt.enc nya berada di directory yang sama dengan program derypt yang diberikan


# analysis & exploit
source code :
```Python
### THIS FUNCTION WILL NOT HELP YOU FIND THE FLAG --LT ########################
def str_xor(secret, key):
    #extend key to secret length
    new_key = key
    i = 0
    while len(new_key) < len(secret):
        new_key = new_key + key[i]
        i = (i + 1) % len(key)        
    return "".join([chr(ord(secret_c) ^ ord(new_key_c)) for (secret_c,new_key_c) in zip(secret,new_key)])
###############################################################################


flag_enc = open('flag.txt.enc', 'rb').read()



def level_1_pw_check():
    user_pw = input("Please enter correct password for flag: ")
    if( user_pw == "ak98" + \
                   "-=90" + \
                   "adfjhgj321" + \
                   "sleuth9000"):
        print("Welcome back... your flag, user:")
        decryption = str_xor(flag_enc.decode(), "utilitarian")
        print(decryption)
        return
    print("That password is incorrect")



level_1_pw_check()

```

ada beberapa cara untuk melakukan ekstrak flag. pertama ambil password lalu masukkan ke program. kedua panggil fungsi decrypt di awal program.
aku akan gunakan cara ke dua saja karena jauh lebih cepat dan sederhana untuk dilakukan. edit dan tambahkan baris ini di awal program
```Python
decryption = str_xor(flag_enc.decode(), "utilitarian")
print(decryption)
```

<img width="404" height="72" alt="image" src="https://github.com/user-attachments/assets/497c811a-0c19-4fdd-9770-57dd4117af8b" />

flag akan di print sebelum program meminta program, ini juga bisa disebut patching. merubah / merusak alur program.
