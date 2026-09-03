# picoCTF2023-Safe Opener 2.md

# overview
hello guys, jadi pada challenge safe opener ini adalah challenge reverse sederhana. namun juga unik. karena file ini adalah hasil decompile dari java. jadi kita butuh java runtime environment untuk menjalankannya. jika sudah punya ghidra biasanya sudah terinstall di linux. jadi tinggal run aja filenya. nah disini filenya menanyakan password 3 kali
tapi sepertinya kita tidak perlu repot repot mencari password nya karena flag nya sudah tertulis hardcoded di source code hasil decompilenya.

# tools
- java / javac
- decompiler explorer (disarankan)
- ghidra (opsional)

# recon
<img width="499" height="399" alt="image" src="https://github.com/user-attachments/assets/c39cb466-af1e-448a-8e66-9e28f659d7bb" />

disini aku diberi file program executable yang di compile dari java. untuk menjalankannya pastikan nama file tersebut adalah **SafeOpener.class** . karena jika namanya
tidak sesuai program akan error ketika dijalankan. untuk menjalankan program ini cukup ketik java nama_program TANPA .CLASS
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(safe_opener)
└> java SafeOpener
Enter password for the safe: 1234
MTIzNA==
Password is incorrect

You have  2 attempt(s) left
Enter password for the safe: 0000
MDAwMA==
Password is incorrect

You have  1 attempt(s) left
Enter password for the safe: 9999
OTk5OQ==
Password is incorrect

You have  0 attempt(s) left  
```
hanya itu yang dilakukan program, menanyakan password 3 kali dan jika kesempatan habis program akan berhenti. jadi satu satunya cara mencari tahu isi program adalah dengan
mendecompile nya menggunakan ghidra.

# exploit
file java ini masih bisa di decompile ghidra karena ghidra sendiri berbasis java. kali ini aku akan menggunakan decompiler explorer , tools decompile online yang juga memiliki
ghidra. setelah di decompile aku copy dan pindahkan seluruh source codenya ke vs codium agar lebih mudah dibaca.  \\

ternyata kita tidak perlu repot repot mencari tahu apa passwordnya karena apa yang kita cari sudah tertulis rapi di source code hasil decompilenya
<img width="526" height="243" alt="image" src="https://github.com/user-attachments/assets/47d197d2-c013-4cc9-8d92-a0905596da30" />
flag : **picoCTF{.............................}**
# conclusion
intinya challenge reverse ini mengenalkan kita pada file program yang di compile dari java dan berjalan diatas java runtime environment. sedikit berbeda perlakuannya dengan file program elf atau exe yang langsung berjalan diatas hardware komputer. jadi penting bagi kita untuk mempelajari tipe arsitektur lain seperti java class ini.
