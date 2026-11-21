# Hidden in the Ports

## deskripsi
Seorang admin lupa menutup sebuah service rahasia di server perusahaan. Service tersebut tidak berjalan di port yang umum, dan petunjuk untuk mengaksesnya tersebar di lebih dari satu tempat.  
Tugasmu: lakukan reconnaissance terhadap server berikut, temukan service yang tersembunyi, lalu kumpulkan seluruh bagian flag.  

Server: [70.70.70.150](70.70.70.150)

Tools yang disarankan: nmap, curl, netcat Format flag: THPCTF{...}

author : AosLie

## Pengumpulan Informasi

saya di beri akses ke sebuah server lokal , yaitu pada ip [70.70.70.150](70.70.70.150). Pemeriksaan pertama dilakukan dengan melakukan scaning ports menggunakan tools `nmap`

```bash
nmap -p- 70.70.70.150
```
result
```
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-11-21 09:36 +07
Nmap scan report for S01060090ea064fc7.vf.shawcable.net (70.70.70.150)
Host is up (0.012s latency).
Not shown: 65532 closed tcp ports (conn-refused)
PORT      STATE SERVICE
2121/tcp  open  ccproxy-ftp
8888/tcp  open  sun-answerbook
31337/tcp open  Elite

Nmap done: 1 IP address (1 host up) scanned in 7.96 seconds
```
hasil scanning menunjukkan bahwa server memiliki 3 port yang terbuka dan masing masing memiliki layanan nya sendiri. untuk mencari tahu version dari layanan tersebut, nmap kembali 
dijalankan dengan flag -sV untuk tiap port nya.

```bash
nmap -sV -p 2121,8888,31337 70.70.70.150
```

result:
```
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-11-21 09:38 +07
Nmap scan report for s01060090ea064fc7.vf.shawcable.net (70.70.70.150)
Host is up (0.030s latency).

PORT      STATE SERVICE VERSION
2121/tcp  open  ftp     ProFTPD 1.3.5
8888/tcp  open  http    Apache httpd 2.4.41 ((Ubuntu))
31337/tcp open  Elite?
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port31337-TCP:V=7.94SVN%I=7%D=11/21%Time=6B01042E%P=x86_64-pc-linux-gnu

---------- fingerprint -------------

SF:(SMBProgNeg,42,"SECRET-SVC\x20v1\.0\x20ready\x20\|\x20part1=THPCTF{nmap
SF:_full_port\x20\|\x20send\x20HELP\n>\x20");
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 126.09 seconds
```
observasi singkat:
- port 2121: ProFTPD 1.3.5
- port 8888: Apache httpd 2.4.41 ((Ubuntu))
- port 31337: Belum diketahui.
terlihat juga hasil scanning, port 31337 mengembalikan sebuah data yang tidak diketahui. `1 service unrecognized despite returning data.` . ini mengindikasikan port 31337
berkemungkinan memiliki layanan informasi/interaktif.

setelah mengetahui seluruh versi pada layanan tiap port. langkah berikutnya adalah mencoba mengakses layanan tersebut sesuai versinya.

**layanan port 2121 (ftp)**
```bash
┌[rotalactf]-[LAPTOP-6QMID52F]-(extended-investigation)
└> nc 70.70.70.150 2121
220 ProFTPD 1.3.5 Server (Corp FTP) [decoy]
hello
530 Please login with USER and PASS.
```
tertulis bahwa layanan ini ternyata hanya decoy. jadi langsung saya skip.

**layanan port 8888 (http)**
```bash
┌[rotalactf]-[LAPTOP-6QMID52F]-(extended-investigation)
└> curl -I 'http://70.70.70.150:8888'
HTTP/1.1 200 OK
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html
X-Passphrase: n0t_4ll_p0rts_4r3_sc4nn3d
X-Note: ask the secret service on the unusual port
Content-Length: 75
Connection: close
```
layanan http ini memberikan response berupa http header. terdapat custom header yang menarik yaitu **X-Passphrase** dan **X-Note**. 

```
X-Passphrase: n0t_4ll_p0rts_4r3_sc4nn3d
X-Note: ask the secret service on the unusual port
```

bisa disimpulkan , saya berhasil mendapatakan sebuah Passphrase , dan clue penting yaitu coba gunakan rahasia ini pada layanan dengan port yang tidak umum. 
jelas , satu satunya layanan dengan port tidak umum disini adalah layanan ketiga , pada port 31337. 

**layanan port 31337**
<p align="center"> <img width="874" height="192" alt="image" src="https://github.com/user-attachments/assets/dca6a071-a468-4591-b79b-f672c7c809d1" /> </p>
