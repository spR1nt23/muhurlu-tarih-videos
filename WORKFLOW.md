# Mühürlü Tarih — günlük üretim ve yükleme

Kanal: Mühürlü Tarih (@muhurlu_tarih) · Kanal kimliği: `UCeb67GPB2yhPnIcxO_jUXsA`
Google hesabı: **selinarica.2007** (Secret Spawn ile aynı hesap). Dil: Türkçe. Saat dilimi: Europe/Istanbul (Studio GMT+03:00).

## Günlük plan (2026-11-11'den itibaren)

Uzun videolar az izlendiği için uzun video **haftada 3 gün**: hedef tarih **Pazartesi, Çarşamba veya Cumartesi** ise.

| Hedef gün | 12:30 | 17:30 | 20:00 | 21:30 |
|---|---|---|---|---|
| Pzt / Çar / Cmt | Shorts | Shorts | **Uzun video (3–4 dk)** | Shorts |
| Diğer günler | Shorts | Shorts | **Shorts** | Shorts |

Görev her akşam 22:37 (İstanbul) çalışır ve **ertesi günün** videolarını üretip ertesi güne planlar. Tarih seçiciden doğru günü seçmeyi unutma. Hedef günün hangi gün olduğunu `date -d tomorrow +%A` (TZ=Europe/Istanbul) ile kontrol et.

## 1. Kurulum (her oturumda)
```bash
git clone --depth 1 https://github.com/spR1nt23/muhurlu-tarih-videos /home/claude/muhurlu-tarih-videos
bash /home/claude/muhurlu-tarih-videos/tools/setup.sh
```
- TTS: `sherpa-onnx==1.13.8` + Piper Türkçe ses `fahrettin` (GitHub release'ten iner). **sherpa-onnx 2.x çalışmıyor**, torch/Coqui kurmaya çalışma (CUDA paketleri yüzünden saatler sürüyor).
- Sayılar seslendirmede yazıyla yazılır (`"say"`), ekranda rakamla gösterilir (`"show"`).

## 2. Konu seç
- `TOPICS.md` dosyasına bak; **daha önce işlenen konuyu tekrar etme**.
- Shorts: tek bir çarpıcı gizem, 30–55 sn. İlk cümle kanca olsun, son cümle izleyiciye soru sorsun.
- Uzun video: 3–4 dk (yaklaşık 30–38 cümle, 5–6 sahne). Daha uzun yapma: kısa ve sıkı anlatım, sahne başına 5–7 cümle. Türk izleyicinin ilgisini çekecek konuları sık seç (Osmanlı, Anadolu, Bizans, Selçuklu gizemleri) ama dünya gizemleri de olur.
- **Gerçekleri web aramasıyla doğrula.** Tartışmalı konularda farklı görüşleri dürüstçe ver; uydurma rakam, alıntı, tarih yok. Komplo teorilerini gerçek gibi sunma.

## 3. Spec yaz ve render et
`content/<TARIH>/` altına JSON spec yaz (örnekler: `content/2026-11-09/`). Biçim `tools/render.py` başında anlatılıyor.
Motifler: document, forest(carve=), hourglass, map(x=), mountains(tent=), parchment, pillars, question, ruins, sea, seal, stars, year(year=).
```bash
cd content/<TARIH>
python3 ../../tools/render.py short1_x.json /home/claude/out/short1_x.mp4
python3 ../../tools/render.py long_x.json /home/claude/out/long_x.mp4   # ~5-6 dk sürer, arka planda çalıştır
python3 ../../tools/thumb.py <motif> "BÜYÜK|SATIR" "küçük satır" ../../videos/<TARIH>/thumb_x.jpg
```
Render'dan sonra her videodan 3-4 kare çıkarıp bak (yazı taşması, üst üste binme). `metadata.json` yaz (başlık, açıklama, saat).
Videoları `videos/<TARIH>/` içine kopyala, commit + `git push origin HEAD:main`. `TOPICS.md`'ye yeni konuları ekle.

## 4. Studio'ya yükle (yerleşik tarayıcı)
1. `https://studio.youtube.com/channel/UCeb67GPB2yhPnIcxO_jUXsA/videos/upload?d=ud` aç. 403 görürsen tarayıcı başka hesapta: pencereyi 1280 yap, profil → Hesap değiştir → selinarica.2007 → Mühürlü Tarih. Studio solda "Your channel Mühürlü Tarih" göstermeli.
2. Dosyayı JS ile ver (tek dosya):
```js
const url='https://raw.githubusercontent.com/spR1nt23/muhurlu-tarih-videos/main/videos/<TARIH>/<DOSYA>.mp4';
const b=await (await fetch(url,{cache:'no-store'})).blob();
const inp=document.querySelector('ytcp-uploads-file-picker input[type=file]')||document.querySelector('input[type=file]');
const dt=new DataTransfer(); dt.items.add(new File([b],'<DOSYA>.mp4',{type:'video/mp4'}));
inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true}));
```
3. Başlık kutusuna tıkla → ctrl+a → yaz. Açıklama kutusuna tıkla → ctrl+a → yaz. Shorts açıklaması `#shorts ` ile (sonda boşluk) biter. **Yazdıktan sonra 2 sn bekleyip ekran görüntüsüyle kontrol et**; yazı geç görünebiliyor, tekrar yazarsan iki kere girer.
4. Bu JS ile kitle + adımlar + saat (TIME örn. `'12:30 PM'`, Studio İngilizce):
```js
const W=ms=>new Promise(r=>setTimeout(r,ms)); const norm=s=>s.replace(/\s+/g,' ').trim(); const TIME='12:30 PM', DATE='Nov 9, 2026';
document.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]').click(); await W(500);
for(let i=0;i<3;i++){document.querySelector('#next-button').click(); await W(1500);}
await W(800); document.querySelector('#second-container-expand-button').click(); await W(1000);
let date=norm(document.querySelector('#datepicker-trigger').innerText);
// tarih yanlışsa: #datepicker-trigger tıkla, takvimde .calendar-day (bugün = .calendar-day.today) seç
document.querySelector('#time-of-day-container input').click(); await W(800);
let it=null; for(let i=0;i<10&&!it;i++){it=[...document.querySelectorAll('tp-yt-paper-item')].filter(e=>e.offsetParent!==null).find(e=>norm(e.innerText)===TIME); if(!it){document.querySelector('#time-of-day-container input').click(); await W(1000);}}
it.scrollIntoView(); it.click(); await W(800);
const time=document.querySelector('#time-of-day-container input').value;
let m=null; if(date===DATE&&norm(time)===TIME){document.querySelector('#done-button').click(); for(let i=0;i<12&&!m;i++){await W(1000); m=document.body.innerText.replace(/\s+/g,' ').match(/Video scheduled.{0,80}|will be set to public on.{0,40}/);}}
({date,time,result:m&&m[0]})
```
   - `result` null ise ekran görüntüsü al: hâlâ Visibility adımındaysan sağ alttaki **Schedule** düğmesine tıkla. "Video processing … will be set to public on …" penceresi de başarı demektir; Close ile kapat.
   - Saat listesindeki metinlerde özel boşluk var; `norm()` şart.
### Daha güvenilir başlık/açıklama yazma (denendi, çalışıyor)
Kutuya koordinatla tıklamak yerine JS ile odaklayıp içeriği seç, sonra `computer type` ile yaz:
```js
window.__mtFocus=(which)=>{const tb=[...document.querySelectorAll('ytcp-social-suggestions-textbox #textbox')].filter(e=>e.offsetParent); const el=which==='title'?tb[0]:tb[1]; el.focus(); const r=document.createRange(); r.selectNodeContents(el); const s=getSelection(); s.removeAllRanges(); s.addRange(r); return tb.length;};
window.__mtFocus('title')   // sonra type: başlık;  ardından __mtFocus('desc') ve type: açıklama
```
Yazdıktan sonra iki kutunun `innerText`'ini okuyup kontrol et, sonra 4. adımdaki JS'i çalıştır. Gezinti (navigate) `window` fonksiyonlarını siler; her videoda yeniden tanımla.

5. Uzun video için kapak: `input#file-loader` (thumbnail) şu an çalışmıyor (kanal doğrulanınca açılır). Doğrulama sonrası aynı DataTransfer yöntemiyle `thumb_x.jpg` verilebilir.
6. Sonraki video için 1'den tekrar. En sonda Content → Shorts ve Videos listelerinde hepsinin **Scheduled** olduğunu kontrol et; "Draft" kalan varsa "Edit draft" ile açıp 4. adımı tekrarla.

## Dikkat
- Escape'e basma (yükleme penceresini kapatır). Yükleme bitmeden sayfadan ayrılma.
- Tarayıcı başka sohbetlerle ortak: her yüklemeden önce kanalın Mühürlü Tarih olduğunu kontrol et.
- Tarayıcı Secret Spawn'dayken `.../UCeb67.../content/shorts` doğrudan açılınca "Oops, something went wrong" verir. Önce `studio.youtube.com` aç, profil → Switch account → Mühürlü Tarih; sonra soldaki **Content** menüsüne tıkla ve Shorts sekmesine geç.
- Görev aynı gün iki kez çalışabilir: `videos/<TARIH>/` varsa önce Studio listelerine bak; dördü de "Scheduled" ise hiçbir şey yükleme.
- Saat listesi (`tp-yt-paper-item`) bazen 800 ms'de açılmıyor; yukarıdaki JS bu yüzden tekrar deneme döngüsü içeriyor.
- Tarayıcı paneli gizliyken başlık kutuları bir süre `offsetParent` null kalabiliyor (`__mtFocus` "reading 'focus'" hatası). Bir ekran görüntüsü al, sonra `__mtFocus`'u tekrar çağır.
- JS içinde 45 sn'den uzun bekleme yapma (araç zaman aşımına düşer). Uzun video planlanınca birkaç dakika "Processing" görünür, sonra Scheduled olur.
- Doğrulanmamış kanalda günlük yükleme sınırı düşük; sınır uyarısı görürsen dur ve raporla.
