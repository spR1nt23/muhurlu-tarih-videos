# Mühürlü Tarih — günlük üretim ve yükleme

Kanal: Mühürlü Tarih (@muhurlu_tarih) · Kanal kimliği: `UCeb67GPB2yhPnIcxO_jUXsA`
Google hesabı: **selinarica.2007** (Secret Spawn ile aynı hesap). Dil: Türkçe. Saat dilimi: Europe/Istanbul (Studio GMT+03:00).

## Her gün: 3 Shorts + 1 uzun video

| Video | Yayın saati |
|---|---|
| Shorts 1 | 12:30 |
| Shorts 2 | 17:30 |
| Uzun video (5–8 dk) | 20:00 |
| Shorts 3 | 21:30 |

Hepsi **yayın günü** tarihine planlanır. Görev gece çalışır; o günün videolarını üretir ve planlar.

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
- Uzun video: 5–8 dk (yaklaşık 60–70 cümle, 8–10 sahne). Türk izleyicinin ilgisini çekecek konuları sık seç (Osmanlı, Anadolu, Bizans, Selçuklu gizemleri) ama dünya gizemleri de olur.
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
const it=[...document.querySelectorAll('tp-yt-paper-item')].filter(e=>e.offsetParent!==null).find(e=>norm(e.innerText)===TIME); it.scrollIntoView(); it.click(); await W(800);
const time=document.querySelector('#time-of-day-container input').value;
let m=null; if(date===DATE&&norm(time)===TIME){document.querySelector('#done-button').click(); for(let i=0;i<12&&!m;i++){await W(1000); m=document.body.innerText.replace(/\s+/g,' ').match(/Video scheduled.{0,80}|will be set to public on.{0,40}/);}}
({date,time,result:m&&m[0]})
```
   - `result` null ise ekran görüntüsü al: hâlâ Visibility adımındaysan sağ alttaki **Schedule** düğmesine tıkla. "Video processing … will be set to public on …" penceresi de başarı demektir; Close ile kapat.
   - Saat listesindeki metinlerde özel boşluk var; `norm()` şart.
5. Uzun video için kapak: `input#file-loader` (thumbnail) şu an çalışmıyor (kanal doğrulanınca açılır). Doğrulama sonrası aynı DataTransfer yöntemiyle `thumb_x.jpg` verilebilir.
6. Sonraki video için 1'den tekrar. En sonda Content → Shorts ve Videos listelerinde hepsinin **Scheduled** olduğunu kontrol et; "Draft" kalan varsa "Edit draft" ile açıp 4. adımı tekrarla.

## Dikkat
- Escape'e basma (yükleme penceresini kapatır). Yükleme bitmeden sayfadan ayrılma.
- Tarayıcı başka sohbetlerle ortak: her yüklemeden önce kanalın Mühürlü Tarih olduğunu kontrol et.
- Doğrulanmamış kanalda günlük yükleme sınırı düşük; sınır uyarısı görürsen dur ve raporla.
