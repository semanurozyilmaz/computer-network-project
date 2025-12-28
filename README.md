# Ağ Gecikme Süresinin Temel Makine Öğrenmesi ile Tahmin Edilmesi

## 🛠️ Kurulum ve Gereksinimler

Bu proje, düşük seviyeli ağ yapılandırmaları gerektirdiği için Linux (tercihen Ubuntu) işletim sisteminde çalıştırılmalıdır.

1. Sistem Bağımlılıkları

Öncelikle sisteminizde Mininet ve iperf yüklü olmalıdır:

sudo apt-get update
sudo apt-get install mininet iperf


## Python Kütüphaneleri

Görselleştirme ve veri işleme için gerekli Python paketlerini yükleyin:

pip install -r requirements.txt


## 📋 Proje Yapısı

simulation1.py: Temel doğrudan bağlantı simülasyonu.

simulation2.py: Switch tabanlı, iperf yüklü simülasyon.

simulation3.py: En gelişmiş, kararlı ve hassas veri seti üreticisi.

requirements.txt: Gerekli Python kütüphaneleri listesi.

## 🏃 Çalıştırma Talimatları

Mininet ağ arayüzlerine doğrudan erişim gerektirdiği için tüm scriptler root (sudo) yetkisiyle çalıştırılmalıdır.

# Simülasyon 1'i başlatmak için
sudo python3 simulation1.py

# Simülasyon 2'yi başlatmak için
sudo python3 simulation2.py

# Simülasyon 3'ü (Final) başlatmak için
sudo python3 simulation3.py


Not: Her simülasyonun sonunda ilgili .csv dosyası (örn: simulation3.csv) otomatik olarak oluşturulacaktır.

## 📊 Ölçülen Metrikler

Veri setleri şu sütunları içerir:

Bağımsız Değişkenler: Bant Genişliği (BW), Gecikme (Delay), Kayıp (Loss), Kuyruk Boyutu (Queue).

Bağımlı Değişkenler: RTT, Jitter, Gerçek Paket Kaybı, Gerçek Verim (Throughput)

