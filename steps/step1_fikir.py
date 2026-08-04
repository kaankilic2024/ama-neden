# -*- coding: utf-8 -*-
"""
ADIM 1 - ICERIK FIKRI URETIMI
Kanal kimligine uygun, daha once kullanilmamis bir video fikri uretir.
"""
import json
import random
from datetime import datetime
from typing import Any, Dict, List

import config
from utils import ai, logger

SISTEM = """Sen bir YouTube merak kanalinin icerik yoneticisisin.

KANAL: {kanal_adi}
TANIM: {kanal_tanimi}

GOREVIN: Kanala uygun, TEK bir "neden boyle?" sorusu bulmak.

IYI BIR SORU NASIL OLUR:
- Izleyicinin daha once dusunmedigi ama duyunca "hakikaten neden?" dedigi
- Gunluk hayatta karsilastigi ama sorgulamadigi bir sey
- Cevabi sasirtici veya zincirleme bir aciklama gerektiren
- Tek cumleyle sorulabilen

ORNEKLER (iyi):
  "Neden uzayda ses duyulmaz?"
  "Ahtapotlarin neden uc kalbi var?"
  "Neden ucaklarin cogu beyaz?"
  "Sahra colu neden bir zamanlar yesildi?"
  "Nokia neden bir anda coktu?"

ORNEKLER (kotu):
  "Uzay nedir?"                      (cok genel)
  "En buyuk gezegen hangisi?"        (soru degil, bilgi yarismasi)
  "Neden mutluyuz?"                  (belirsiz, felsefi)

DOGRULUK KURALLARI:
- SADECE genel kabul gormus, yaygin bilinen bilgiler onerebilirsin.
- Emin olmadigin hicbir sey yazma. Supheliysen o fikri hic onerme.
- Komplo teorisi, kanitlanmamis iddia, "gizlenen gercek" turu icerik URETME.
- Tibbi tavsiye, saglik iddiasi, yatirim onerisi YASAK.

KACINILACAK KONULAR:
- Guncel siyaset, dini tartisma, etnik konular
- Yasayan kisiler hakkinda iddia
- Cinsel icerik, siddet detayi

Cevabini SADECE su JSON formatinda ver, baska hicbir sey yazma:
{{
  "konu": "Videonun sorusu, soru formatinda (max 10 kelime)",
  "alan": "Hangi alandan (uzay/doga/cografya/teknoloji/cokus/insan)",
  "ozet": "Cevabin ozeti, 2-3 cumle",
  "mesaj": "Izleyicinin ogrenecegi ana bilgi, tek cumle",
  "neden_ilgi_ceker": "Neden merak uyandirir, tek cumle",
  "guven_seviyesi": "yuksek / orta -- bu bilginin ne kadar yaygin kabul gordugu",
  "anahtar_kelimeler": ["5", "adet", "turkce", "anahtar", "kelime"]
}}"""

ISTEK = """Video tipi: {tip_ad} ({en_boy}, yaklasik {sure} saniye)
Bu tip icin uygun konu turleri: {konu_tipleri}
Bu videoda su tur one cikacak: {secilen_tur}

BUGUNUN ALANI: {tema_ad}
Bu alandan bir soru bul: {tema_aciklama}

Daha once kullanilmis konular (bunlara benzeme):
{gecmis}

Simdi yeni ve ozgun bir "neden" sorusu uret."""

MOCK_FIKIR = {
    "konu": "Neden ucaklarin cogu beyaz?",
    "alan": "teknoloji",
    "ozet": "Beyaz boya gunes isigini yansitarak govdeyi serin tutar ve "
            "yakit tasarrufu saglar. Ayrica catlak, yag sizintisi gibi "
            "sorunlari fark etmeyi kolaylastirir ve boya solmasi az olur.",
    "mesaj": "Ucak renginin sebebi estetik degil, tamamen pratik.",
    "neden_ilgi_ceker": "Herkes gormus ama kimse sorgulamamis bir detay.",
    "guven_seviyesi": "yuksek",
    "anahtar_kelimeler": ["ucak", "neden", "merak", "havacilik", "ama neden"],
}


# ------------------------------------------------------------------ gecmis
def _gecmis_oku() -> List[Dict[str, Any]]:
    try:
        return json.loads(config.FIKIR_GECMISI.read_text(encoding="utf-8"))
    except Exception:
        return []


def _gecmis_yaz(kayit: Dict[str, Any]) -> None:
    gecmis = _gecmis_oku()
    gecmis.append(kayit)
    gecmis = gecmis[-200:]          # son 200 kayit yeter
    config.FIKIR_GECMISI.write_text(
        json.dumps(gecmis, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def gunun_temasi() -> tuple:
    """Haftanin gunune gore tema secer.

    Cesitlilik saglar ama her gun sabit bir alan oldugu icin kanal
    tamamen dagilmaz. Tek bir gunde uretilen videolar ayni alandan olur.
    """
    gun = datetime.now().weekday()          # 0 = Pazartesi
    return config.TEMALAR.get(gun, config.TEMALAR[6])


def _gecmis_metni(adet: int = 30) -> str:
    gecmis = _gecmis_oku()[-adet:]
    if not gecmis:
        return "(henuz kullanilmis konu yok)"
    return "\n".join(f"- {k['konu']}" for k in gecmis)


# ------------------------------------------------------------------ ana fonksiyon
def fikir_uret(video_tipi: str) -> Dict[str, Any]:
    """video_tipi: 'shorts' veya 'uzun'"""
    if video_tipi not in config.VIDEO_TIPLERI:
        raise ValueError(f"Bilinmeyen video tipi: {video_tipi}")

    profil = config.VIDEO_TIPLERI[video_tipi]
    secilen_tur = random.choice(profil["konu_tipleri"])
    tema_ad, tema_aciklama = gunun_temasi()

    logger.bilgi(
        f"Fikir araniyor... (tip: {profil['ad']}, alan: {tema_ad}, "
        f"tur: {secilen_tur})"
    )

    sistem = SISTEM.format(
        kanal_adi=config.KANAL_ADI, kanal_tanimi=config.KANAL_TANIMI
    )
    istek = ISTEK.format(
        tip_ad=profil["ad"],
        en_boy=profil["en_boy"],
        sure=profil["hedef_saniye"],
        konu_tipleri=", ".join(profil["konu_tipleri"]),
        secilen_tur=secilen_tur,
        tema_ad=tema_ad,
        tema_aciklama=tema_aciklama,
        gecmis=_gecmis_metni(),
    )

    fikir = ai.sor(sistem, istek, sicaklik=1.0, mock_cevap=MOCK_FIKIR)

    # Zorunlu alan kontrolu
    for alan in ("konu", "ozet", "mesaj", "anahtar_kelimeler"):
        if not fikir.get(alan):
            raise ai.AIHatasi(f"Fikirde '{alan}' alani eksik: {fikir}")

    fikir["video_tipi"] = video_tipi
    fikir["konu_turu"] = secilen_tur
    fikir["tema"] = tema_ad
    fikir["tarih"] = datetime.now().isoformat(timespec="seconds")

    _gecmis_yaz({"konu": fikir["konu"], "tarih": fikir["tarih"], "tip": video_tipi})

    logger.ok(f"Fikir hazir: {fikir['konu']}")
    return fikir
