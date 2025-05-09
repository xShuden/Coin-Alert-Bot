# ListedOn.org & Binance Telegram Alert Bot

Bu Telegram botu, [listedon.org](https://listedon.org/) web sitesinde yeni listelenen kripto paraları takip eder ve bu paraların [Binance](https://www.binance.com/) borsasında zaten listelenmiş olup olmadığını kontrol eder. Eğer bir coin hem listedon.org'da yeni listelenmiş hem de Binance'te mevcutsa, bot bir Telegram mesajı ile bildirim gönderir.

## Özellikler

- Belirli aralıklarla `listedon.org`'u yeni coin listelemeleri için kontrol eder.
- Tespit edilen coinlerin Binance API'si aracılığıyla Binance'te listelenip listelenmediğini doğrular.
- Eşleşme durumunda yapılandırılan Telegram sohbetine anlık bildirimler gönderir.
- Daha önce bildirilen coinlerin kaydını tutarak mükerrer bildirimleri önler (`notified_tickers.json`).
- Docker ve Docker Compose ile kolayca dağıtılabilir ve yönetilebilir.

## Gereksinimler

- Python 3.8+ (Python 3.9 ile test edilmiştir)
- Pip (Python paket yöneticisi)
- Docker (Önerilir, sürekli çalıştırma ve kolay dağıtım için)
- Docker Compose (Önerilir)

## Kurulum

1.  **Projeyi Klonlayın (veya İndirin):**
    ```bash
    git clone <repository_url> # Eğer GitHub'a yüklerseniz bu komutu kullanın
    cd <proje_klasoru>
    ```

2.  **`.env` Dosyasını Oluşturun:**
    Proje ana dizininde `.env` adında bir dosya oluşturun ve aşağıdaki değişkenleri kendi bilgilerinizle doldurun:
    ```env
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
    TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID_HERE"
    # NOTIFIED_TICKERS_FILE="notified_tickers.json" # Bu satır varsayılan olarak bot.py içinde ayarlı, isterseniz değiştirebilirsiniz.
    ```
    - `YOUR_TELEGRAM_BOT_TOKEN_HERE`: Telegram BotFather'dan aldığınız bot token'ınız.
    - `YOUR_TELEGRAM_CHAT_ID_HERE`: Botun mesaj göndereceği Telegram kullanıcı veya grup ID'niz.

3.  **`notified_tickers.json` Dosyasını Oluşturun:**
    Proje ana dizininde `notified_tickers.json` adında boş bir JSON dosyası oluşturun. Bot ilk çalıştığında bu dosya yoksa oluşturulur, ancak Docker volume ile düzgün çalışması için önceden boş olarak var olması daha iyidir.
    ```json
    []
    ```

## Çalıştırma

### A. Yerel Olarak (Docker Olmadan)

1.  **Sanal Ortam Oluşturun ve Aktif Edin (Önerilir):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux için
    # venv\Scripts\activate    # Windows için
    ```

2.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Botu Başlatın:**
    ```bash
    python3 bot.py
    ```
    Bot terminalde çalışmaya başlayacak ve logları gösterecektir. Durdurmak için `CTRL+C` kullanın.

### B. Docker ile (Önerilir)

Docker'ın ve Docker Compose'un sisteminizde kurulu olduğundan emin olun.

1.  **Docker İmajını Build Edin:**
    Proje ana dizinindeyken aşağıdaki komutu çalıştırın:
    ```bash
    docker-compose build
    ```
    Bu komut, `Dockerfile` dosyasını kullanarak bot için bir Docker imajı oluşturacaktır.

2.  **Botu Arka Planda Başlatın:**
    ```bash
    docker-compose up -d
    ```
    Bot, Docker container'ı içinde arka planda çalışmaya başlayacaktır.

3.  **Logları Görüntüleyin (İsteğe Bağlı):**
    Botun loglarını gerçek zamanlı olarak görmek isterseniz:
    ```bash
    docker-compose logs -f
    ```
    Loglardan çıkmak için `CTRL+C` kullanın (bot çalışmaya devam edecektir).

4.  **Botu Durdurun:**
    Botu ve ilişkili Docker container'ını durdurmak için:
    ```bash
    docker-compose down
    ```

## Dosya Yapısı

```
.
├── .env                # Çevre değişkenleri (Telegram token, chat ID)
├── .gitignore          # Git tarafından izlenmeyecek dosyalar
├── Dockerfile          # Bot için Docker imajını oluşturma talimatları
├── bot.py              # Ana Telegram bot mantığı, zamanlama, komutlar
├── scraper.py          # listedon.org'dan veri çekme (scraping) mantığı
├── binance_checker.py  # Binance API ile coin kontrolü mantığı
├── requirements.txt    # Python bağımlılıkları
├── notified_tickers.json # Daha önce bildirilen coinlerin listesi
└── docker-compose.yml  # Docker container'ını kolayca yönetmek için yapılandırma
└── README.md           # Bu dosya
```

## Docker Yapılandırması

-   **`Dockerfile`:** Python 3.9-slim tabanlı bir imaj kullanır, gerekli bağımlılıkları kurar ve bot uygulamasını container içine kopyalar. Container başladığında `python3 bot.py` komutunu çalıştırır.
-   **`docker-compose.yml`:**
    -   `telegram-bot` adında bir servis tanımlar.
    -   Mevcut dizindeki `Dockerfile`'ı kullanarak imajı build eder.
    -   `.env` dosyasındaki değişkenleri container'a aktarır.
    -   `notified_tickers.json` dosyasının kalıcılığını sağlamak için bir Docker volume kullanır. Bu sayede container yeniden başlasa bile bildirilen ticker'lar kaybolmaz.
    -   `restart: unless-stopped` politikası ile, container bir hata nedeniyle durursa veya sunucu yeniden başlarsa otomatik olarak yeniden başlatılır.

## Katkıda Bulunma

Katkılarınız her zaman beklerim! Lütfen bir issue açın veya bir pull request gönderin.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın (eğer oluşturulursa).
