# Agentic RAG Chatbot Projesi Sunumu

## 1. Proje Tanıtımı
- **Proje Adı**: Agentic RAG Chatbot
- **Amaç**: Gelişmiş bir sohbet botu sistemi oluşturmak
- **Temel Özellikler**:
  - Doküman işleme ve analiz
  - Vektör tabanlı semantik arama
  - Konuşma hafızası
  - RESTful API endpoints
  - Doküman yükleme desteği

## 2. RAG (Retrieval-Augmented Generation) Nedir?
- **Tanım**: RAG, büyük dil modellerinin (LLM) bilgi tabanını genişletmek için kullanılan bir tekniktir
- **Çalışma Prensibi**:
  1. **Retrieval (Alım) Aşaması**:
     - Kullanıcı sorusu alınır
     - Soru vektöre dönüştürülür
     - Vektör veritabanında benzer içerikler aranır
     - En alakalı dokümanlar seçilir
  
  2. **Augmentation (Zenginleştirme) Aşaması**:
     - Seçilen dokümanlar bağlama eklenir
     - Prompt oluşturulur
     - LLM için zenginleştirilmiş bağlam hazırlanır
  
  3. **Generation (Üretim) Aşaması**:
     - LLM zenginleştirilmiş bağlamı kullanır
     - Daha doğru ve bağlama uygun yanıtlar üretir
     - Kaynakları referans gösterir

- **Neden Önemli?**:
  - Güncel bilgilere erişim sağlar
  - Yanıtların doğruluğunu artırır
  - Kaynak gösterimi yapabilir
  - Özelleştirilmiş bilgi tabanı oluşturma imkanı sunar
  - Hallüsinasyonları azaltır
  - Domain-spesifik bilgi sağlar

## 3. Agentic Özellikler
- **Tanım**: Agentic, yapay zeka sistemlerinin otonom kararlar alabilme ve karmaşık görevleri planlayabilme yeteneğidir
- **Temel Özellikler**:
  1. **Otonom Karar Verme**:
     - Kullanıcı girdisine göre en uygun aksiyonu seçme
     - Karmaşık görevleri alt görevlere bölme
     - Hata durumlarında alternatif çözümler üretme
  
  2. **Araç Kullanımı**:
     - Web arama yapabilme
     - Doküman işleme
     - Veri analizi
     - Hesaplama yapabilme
  
  3. **Bağlam Yönetimi**:
     - Konuşma geçmişini hatırlama
     - Kullanıcı tercihlerini öğrenme
     - Oturum yönetimi
  
  4. **Öğrenme ve Adaptasyon**:
     - Kullanıcı geri bildirimlerinden öğrenme
     - Performans iyileştirme
     - Yeni senaryolara adaptasyon

- **Avantajları**:
  - Daha akıllı ve bağımsız sistemler
  - Karmaşık görevleri otomatikleştirme
  - Kullanıcı deneyimini iyileştirme
  - Sürekli gelişim ve öğrenme

## 4. Web Search Tool Entegrasyonu
- **Amaç**: Gerçek zamanlı ve güncel bilgilere erişim
- **Kullanım Alanları**:
  - Güncel haberler
  - Dinamik içerikler
  - Gerçek zamanlı veriler
- **Avantajları**:
  - Geniş bilgi kaynağı
  - Sürekli güncellenen içerik
  - Çeşitli kaynaklardan bilgi toplama

## 5. Teknik Altyapı
### 5.1 Kullanılan Teknolojiler
- **Backend**: FastAPI (Python)
- **Frontend**: React,Vite
- **Veritabanı**: ChromaDB (Vektör veritabanı)
- **AI Modeli**: GPT-4o-mini
- **Embedding Model**: text-embedding-3-small

### 5.2 Vektör Veritabanı ve Embedding
#### Vektör Veritabanı Nedir?
- **Tanım**: Metin verilerini vektör formatında saklayan ve benzerlik araması yapabilen özel veritabanı sistemidir
- **Çalışma Prensibi**:
  1. **Veri Saklama**:
     - Metinler vektörlere dönüştürülür
     - Her vektör, metnin anlamsal özelliklerini temsil eder
     - Vektörler yüksek boyutlu uzayda saklanır
  
  2. **Benzerlik Arama**:
     - Kosinüs benzerliği kullanılır
     - En yakın komşu (k-NN) algoritması
     - Hızlı indeksleme ve arama
  
  3. **Avantajları**:
     - Semantik arama yapabilme
     - Yüksek performanslı sorgulama
     - Ölçeklenebilir yapı
     - Anlamsal ilişkileri yakalayabilme

#### Embedding Nedir?
- **Tanım**: Metin verilerini sayısal vektörlere dönüştürme işlemidir
- **Nasıl Çalışır?**:
  1. **Metin İşleme**:
     - Metin tokenlara bölünür
     - Her token vektöre dönüştürülür
     - Cümle/paragraf seviyesinde birleştirme
  
  2. **Vektör Özellikleri**:
     - Boyut: Genellikle 1536 veya 3072
     - Her boyut bir özelliği temsil eder
     - Benzer metinler benzer vektörlere sahip olur
  
  3. **Kullanım Alanları**:
     - Semantik arama
     - Benzerlik analizi
     - Sınıflandırma
     - Kümeleme

#### Projemizde Kullanımı
- **ChromaDB Entegrasyonu**:
  - Dokümanları vektörlere dönüştürme
  - Vektör veritabanında saklama
  - Benzerlik bazlı arama
  - Otomatik indeksleme

- **Embedding Modeli**:
  - text-embedding-3-small kullanımı
  - 1536 boyutlu vektörler
  - Yüksek doğruluk oranı
  - Hızlı dönüşüm

- **Performans Optimizasyonu**:
  - Batch işleme
  - Önbellekleme
  - Paralel işleme
  - Asenkron dönüşümler

### 5.3 Proje Mimarisi
```
chatbot-v2/
├── app/                    # Ana uygulama kodu
│   ├── main.py            # FastAPI uygulaması
│   ├── config.py          # Konfigürasyon ayarları
│   ├── rag_chain.py       # RAG zinciri implementasyonu
│   └── vector_store.py    # Vektör depolama işlemleri
├── data/                  # Veri depolama
├── uploads/              # Yüklenen dosyalar
├── static/              # Statik dosyalar
└── templates/           # HTML şablonları
```

## 6. Temel Özellikler ve İşlevler
### 6.1 Doküman İşleme
- PDF, TXT, DOCX dosya desteği
- Otomatik metin çıkarma
- Vektör dönüşümü ve indeksleme

### 6.2 Sohbet Özellikleri
- Bağlama duyarlı yanıtlar
- Konuşma geçmişi yönetimi
- Kaynak gösterimi
- Gerçek zamanlı web araması

### 6.3 API Endpoints
- **POST `/chat`**
  - Sohbet mesajları göndermek için
  - Request Body:
    ```json
    {
      "message": "Kullanıcı mesajı",
      "session_id": "Opsiyonel oturum ID"
    }
    ```
  - Response:
    ```json
    {
      "response": "Bot yanıtı",
      "sources": ["Kaynak 1", "Kaynak 2"],
      "session_id": "Oturum ID"
    }
    ```

- **POST `/upload`**
  - Doküman yüklemek için
  - Content-Type: `multipart/form-data`
  - Form Fields:
    - `file`: Yüklenecek dosya (PDF, TXT, DOCX)
  - Response:
    ```json
    {
      "filename": "yüklenen_dosya.pdf",
      "status": "success",
      "message": "Dosya başarıyla yüklendi"
    }
    ```

- **GET `/health`**
  - Sistem durumunu kontrol etmek için
  - Response:
    ```json
    {
      "status": "healthy",
      "version": "1.0.0",
      "uptime": "2h 30m"
    }
    ```

- **GET `/`**
  - Web arayüzünü görüntülemek için
  - HTML response döndürür

- **GET `/static/{path}`**
  - Statik dosyalara erişim için
  - CSS, JavaScript ve diğer statik dosyalar

## 7. Güvenlik ve Performans
- API anahtarı yönetimi
- Dosya yükleme güvenliği
- Önbellek mekanizmaları
- Hata yönetimi

## 8. Gelecek Geliştirmeler
- Çoklu dil desteği
- Gelişmiş analitik özellikleri
- Kullanıcı yönetimi
- Daha fazla dosya formatı desteği

## 9. Sonuç
- Modern ve ölçeklenebilir mimari
- Güçlü AI entegrasyonu
- Esnek ve genişletilebilir yapı
- Kullanıcı dostu arayüz 