# danakaget.md

# deskripsi
author : mas bagus
deskripsi : solve coba  
**link terlampir : https://seafile.bagusarya.me/f/b5f3fb4d4557485b8008/?dl=1**

# note 
chall misc / reverse-web . campuran banget. no ai btw.

# step by step
link terlampir merupakan link download file `foto.jpg` 

<p align="center"><img width="60%" height="481" alt="image" src="https://github.com/user-attachments/assets/93c66876-7a54-4598-86b4-defd2cd18c00" /></p>

kayanya lebih baik tidak perlu dibuka. intinya karena ini file foto jadi perlu di analisis dengan **tools forensic dasar like exiftool ,strings** dan lainnya. hasil exiftool 
cukup menarik karena metadatanya terkesan ramai bahkan ada claude yang numpang nama di metadatanya hm. lanjut analisis aku menemukan hal menarik lain di hasil strings foto. 

<p align="center"><img width="60%" height="167" alt="image" src="https://github.com/user-attachments/assets/a0f4d589-e3fc-4656-8fd6-749765ed8c24" /></p>

link : https://seafile.bagusarya.me/f/2e003b3c99fa416bad47/

link tersebut mengarah ke seafile yang menyimpan file FlagVault.apk . aku download di laptop dan coba baca isinya pakai jadx.

di source codenya ada 4 class 
- CryptoVault
- MainActivity
- R
- VMDetect

aku coba baca dari paling atas, karena di jadx urutannya sesuai abjad. dan sepertinya class tersebut memang harus dibuka. 

berikut isinya : 
```java
package id.bagusarya.goods;

import java.math.BigInteger;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.spec.RSAPrivateKeySpec;
import javax.crypto.Cipher;

/* loaded from: classes.dex */
public final class CryptoVault {
    public static final byte[] CIPHERTEXT = {96, 6, -121, -81, -38, -111, 28, -20, -25, 114, -53, -82, 22, 18, -108, 109, -2, -105, -122, 72, 40, -25, -41, -69, -93, 114, -94, -69, -112, -99, -5, -127, 15, -46, -59, 56, 123, 121, 117, 115, 65, 40, 118, 64, -116, -79, 106, -69, 24, -90, -103, 73, 96, 76, 125, -43, 55, -31, -108, -78, -12, -97, Byte.MIN_VALUE, 112, -116, 36, -11, 108, -28, 77, -8, -99, 113, 2, -84, -8, -82, 109, -22, 12, -16, -68, -124, -60, -52, 78, 112, -114, 56, 36, -87, 110, -64, -61, 12, -76, -32, -39, 102, -85, -71, -4, 123, -81, 40, -22, 33, -117, -120, -60, -61, 104, -80, 70, 57, -13, 6, -74, 8, -74, 80, 89, -127, -12, 33, 43, -48, -39};
    public static final String RSA_MODULUS = "110631189337251177277513568399365666249546371437903762416930468265859998534607810520458101627673347857876464429762153951912413366352852387370962543641826137169267003485292227918052929701748397463975909718367158341323501972358183213186703762195211793266287459872143943467552081052433106823114268530129472127787";
    public static final String RSA_PRIVATE_D = "12535624334626657345664521704284441423457456922011586427638214403196306653005136044141810926455319608657561756800185471518403064811271218222023709493632615743013930491517880845669297346562955339914129283072179073576914482033811473706048077795846940536552963239730856487678194641357607674901668238393789918801";

    private CryptoVault() {
    }

    public static String getVaultUrl() throws Exception {
        PrivateKey generatePrivate = KeyFactory.getInstance("RSA").generatePrivate(new RSAPrivateKeySpec(new BigInteger(RSA_MODULUS), new BigInteger(RSA_PRIVATE_D)));
        Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
        cipher.init(2, generatePrivate);
        return new String(cipher.doFinal(CIPHERTEXT), "UTF-8");
    }
}
```

isinya RSA.  singkatnya yang dilakukan class ini adalah mendekripsi Ciphertext tersebut yang sebelumnya di encrypt dengan RSA. jika class ini di eksekusi maka string getVaultUrl nya akan
ter deskripsi dan jadi return value. 

jadi class ini ku pindah ke VS Codium dan ku tambahkan ini di bawah static string terakhir. 

```java
    public static void main(String[] args) throws Exception{
        System.out.println(getVaultUrl());}
```
itu tadi adalah code java sederhana, standart main class aja si. tapi, aku buat melakukan print class getvaulturl tadi agar hasil deskripsinya tercetak di layar 


by the way baris pertama bagian `//package id.bagusarya.goods;` itu harus di komentar atau hapus aja, karena kalau nggak bakalan error. 

maka full codenya akan jadi gini
```
//package id.bagusarya.goods;

import java.math.BigInteger;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.spec.RSAPrivateKeySpec;
import javax.crypto.Cipher;

/* loaded from: classes.dex */
public final class CryptoVault {
    public static final byte[] CIPHERTEXT = {96, 6, -121, -81, -38, -111, 28, -20, -25, 114, -53, -82, 22, 18, -108, 109, -2, -105, -122, 72, 40, -25, -41, -69, -93, 114, -94, -69, -112, -99, -5, -127, 15, -46, -59, 56, 123, 121, 117, 115, 65, 40, 118, 64, -116, -79, 106, -69, 24, -90, -103, 73, 96, 76, 125, -43, 55, -31, -108, -78, -12, -97, Byte.MIN_VALUE, 112, -116, 36, -11, 108, -28, 77, -8, -99, 113, 2, -84, -8, -82, 109, -22, 12, -16, -68, -124, -60, -52, 78, 112, -114, 56, 36, -87, 110, -64, -61, 12, -76, -32, -39, 102, -85, -71, -4, 123, -81, 40, -22, 33, -117, -120, -60, -61, 104, -80, 70, 57, -13, 6, -74, 8, -74, 80, 89, -127, -12, 33, 43, -48, -39};
    public static final String RSA_MODULUS = "110631189337251177277513568399365666249546371437903762416930468265859998534607810520458101627673347857876464429762153951912413366352852387370962543641826137169267003485292227918052929701748397463975909718367158341323501972358183213186703762195211793266287459872143943467552081052433106823114268530129472127787";
    public static final String RSA_PRIVATE_D = "12535624334626657345664521704284441423457456922011586427638214403196306653005136044141810926455319608657561756800185471518403064811271218222023709493632615743013930491517880845669297346562955339914129283072179073576914482033811473706048077795846940536552963239730856487678194641357607674901668238393789918801";

    private CryptoVault() {
    }

    public static String getVaultUrl() throws Exception {
        PrivateKey generatePrivate = KeyFactory.getInstance("RSA").generatePrivate(new RSAPrivateKeySpec(new BigInteger(RSA_MODULUS), new BigInteger(RSA_PRIVATE_D)));
        Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
        cipher.init(2, generatePrivate);
        return new String(cipher.doFinal(CIPHERTEXT), "UTF-8");
    }
    public static void main(String[] args) throws Exception{
        System.out.println(getVaultUrl()); 
    }
}
```

lalu tinggal di compile pakai javac dan run pakai java
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(folder)
└> javac CryptoVault.java
┌[rotalactf]-[LAPTOP-6QMID52F]-(folder)
└> java CryptoVault
https://spartaf.bagusarya.me
```
another link

<p align="center"><img width="60%" height="569" alt="image" src="https://github.com/user-attachments/assets/5cbbd773-af2a-4b44-a4b6-197b6751368e" /></p>

tadi flagnya bukan itu , tapi yaudah si. 


flag = `Goods{........................................ini_link_duit_gratis_btw.........................................}`
flag sebelumnya : = `Goods{4njAy_KER3N_81s4_REvERsE_5PAR7@}` untung masi kesimpen wkwk


# kesimpulan
chall ini merupakan gabungan dari kategori reverse-web sederhana. serta sedikit pemahaman mengenai bahasa java. funfact: ada beberapa alternatif untuk mengerjakan chall ini
seperti menulis ulang decrypter rsa itu di python atau hanya menjalankan apknya. tapi cara ku ya gini deh. untuk penjelasan nya CMIIW ya. 
