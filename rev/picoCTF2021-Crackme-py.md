# picoCTF2021-Crackme-py.md
# overview
<img width="493" height="263" alt="image" src="https://github.com/user-attachments/assets/8635db15-e070-41a3-9408-c3196c165366" />
kita diberi source code python dan harus mendecode flag yang sudah ada di source code tersebut.

# recon
pertama aku download file dari picoctf dan rupanya itu adalah file source code bahasa python 
```Python
# Hiding this really important number in an obscure piece of code is brilliant!
# AND it's encrypted!
# We want our biggest client to know his information is safe with us.
bezos_cc_secret = "A:4@r%uL`>0c0Abc?FE0g`_47fgaagg6ffN"

# Reference alphabet
alphabet = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"+ \
            "[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"



def decode_secret(secret):
    """ROT47 decode

    NOTE: encode and decode are the same operation in the ROT cipher family.
    """

    # Encryption key
    rotate_const = 47

    # Storage for decoded secret
    decoded = ""

    # decode loop
    for c in secret:
        index = alphabet.find(c)
        original_index = (index + rotate_const) % len(alphabet)
        decoded = decoded + alphabet[original_index]

    print(decoded)



def choose_greatest():
    """Echo the largest of the two numbers given by the user to the program

    Warning: this function was written quickly and needs proper error handling
    """

    user_value_1 = input("What's your first number? ")
    user_value_2 = input("What's your second number? ")
    greatest_value = user_value_1 # need a value to return if 1 & 2 are equal

    if user_value_1 > user_value_2:
        greatest_value = user_value_1
    elif user_value_1 < user_value_2:
        greatest_value = user_value_2

    print( "The number with largest positive magnitude is "
        + str(greatest_value) )



choose_greatest()
```
terdapat dua fungsi yang dideklarasikan yaitu `choose_greatest` dan `decode_secret`. di paling atas program juga terdapat deklarasi variabel lyang sudah diinisiasi dengan string
yang terlihat random. kemungkinan itu flag yang di encode : ``bezos_cc_secret = A:4@r%uL`>0c0Abc?FE0g`_47fgaagg6ffN"``

namun sepertinya chall ini membagikan apa encode yang digunakan , bahkan kode untuk mendecodenya. ini terbukti di fungsi decode_secret yang tidak di panggil
```Python
def decode_secret(secret):
    """ROT47 decode

    NOTE: encode and decode are the same operation in the ROT cipher family.
    """

    # Encryption key
    rotate_const = 47

    # Storage for decoded secret
    decoded = ""

    # decode loop
    for c in secret:
        index = alphabet.find(c)
        original_index = (index + rotate_const) % len(alphabet)
        decoded = decoded + alphabet[original_index]

    print(decoded)

```
ini adalah decode ROT47 . alias pergeseran karakter sebanyak 47 kali. dan encode decode menggunakan operasi yang sama di keluarga ROT Cipher.
kita bisa langsung mencoba menggunakan program decode ini.
# exploit
cara menggunakan fungsi `decode_secret()` ini adalah dengan mengetik ulang nama fungsi itu dengan argumen ciphertext nya.  

cukup tambahkan `decode_secret(bezos_cc_secret)` di atas `choose_greatest()` atau hapus saja `choose_greatest()` dan ganti dengan fungsi decode tersebut.
# conclusion
