# picoCTF2022-bloat.py

# overview
<img width="448" height="299" alt="image" src="https://github.com/user-attachments/assets/90fa868e-98b4-4c09-8e40-10b176652337" />

pada challenge ini aku diberi file flag terenkripsi dan source code yang .. hampir terencode wkwkwkkw. namun hanya butuh sedikit logika untuk solvenya. sederhana saja.

# analysis & exploit
pertama aku coba jalankan pythonnya dan program ini meminta password. untuk melanjutkan analisis aku akan coba baca source codenya.

<img width="407" height="71" alt="image" src="https://github.com/user-attachments/assets/469ce499-a7b3-4f86-8bf9-f81cd12f3ad3" />

source code python:
```Python
import sys
a = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"+ \
            "[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ "
def arg133(arg432):
  if arg432 == a[71]+a[64]+a[79]+a[79]+a[88]+a[66]+a[71]+a[64]+a[77]+a[66]+a[68]:
    return True
  else:
    print(a[51]+a[71]+a[64]+a[83]+a[94]+a[79]+a[64]+a[82]+a[82]+a[86]+a[78]+\
a[81]+a[67]+a[94]+a[72]+a[82]+a[94]+a[72]+a[77]+a[66]+a[78]+a[81]+\
a[81]+a[68]+a[66]+a[83])
    sys.exit(0)
    return False
def arg111(arg444):
  return arg122(arg444.decode(), a[81]+a[64]+a[79]+a[82]+a[66]+a[64]+a[75]+\
a[75]+a[72]+a[78]+a[77])
def arg232():
  return input(a[47]+a[75]+a[68]+a[64]+a[82]+a[68]+a[94]+a[68]+a[77]+a[83]+\
a[68]+a[81]+a[94]+a[66]+a[78]+a[81]+a[81]+a[68]+a[66]+a[83]+\
a[94]+a[79]+a[64]+a[82]+a[82]+a[86]+a[78]+a[81]+a[67]+a[94]+\
a[69]+a[78]+a[81]+a[94]+a[69]+a[75]+a[64]+a[70]+a[25]+a[94])
def arg132():
  return open('flag.txt.enc', 'rb').read()
def arg112():
  print(a[54]+a[68]+a[75]+a[66]+a[78]+a[76]+a[68]+a[94]+a[65]+a[64]+a[66]+\
a[74]+a[13]+a[13]+a[13]+a[94]+a[88]+a[78]+a[84]+a[81]+a[94]+a[69]+\
a[75]+a[64]+a[70]+a[11]+a[94]+a[84]+a[82]+a[68]+a[81]+a[25])
def arg122(arg432, arg423):
    arg433 = arg423
    i = 0
    while len(arg433) < len(arg432):
        arg433 = arg433 + arg423[i]
        i = (i + 1) % len(arg423)        
    return "".join([chr(ord(arg422) ^ ord(arg442)) for (arg422,arg442) in zip(arg432,arg433)])
arg444 = arg132()
arg432 = arg232()
arg133(arg432)
arg112()
arg423 = arg111(arg444)
print(arg423)
sys.exit(0)


```

sedikit obfuscation...  
np

cukup cari saja program yang menampilkan ciri ciri if else perbandingan string. dan itu ada di :

```Python
def arg133(arg432):
  if arg432 == a[71]+a[64]+a[79]+a[79]+a[88]+a[66]+a[71]+a[64]+a[77]+a[66]+a[68]:
    return True
  else:
```
kenapa aku tahu kalau ini if else? jelas karena ada kata `if` ,`else` bahkan `:` nya juga. selain itu ini membandingkan variabel `arg432` dengan string yang ga jelas itu.
setelah referensi variabel itu di telusuri , ternyata arg432 adalah input user. 

```Python
def arg232():
  return input(a[47]+a[75] -------->

###########

arg432 = arg232()
```
dan jika input user valid atau sama dengan string `a[71]+a[64]+a[79]+a[79]+a[88]+a[66]+a[71]+a[64]+a[77]+a[66]+a[68]` maka fungsi validasi ini akan mengenmbalikan nilai true.
tidak salah lagi string itu adalah password. cara ekstraknya cukup sederhana. copy variabel a dan string. lalu lakukan print seperti biasannya.

```Python

a = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"+ \
            "[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ "

print(a[71]+a[64]+a[79]+a[79]+a[88]+a[66]+a[71]+a[64]+a[77]+a[66]+a[68])

```
result : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(bloat)
└> python3 translate.py
happychance
```

ternyata string itu adalah `happychance` hadeh. coba input kan saja.

<img width="416" height="86" alt="image" src="https://github.com/user-attachments/assets/ab66d556-5b42-48ff-bf5e-32596070c271" />

menarik

