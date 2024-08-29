# s3r4ph1

**s3r4ph1** is a Python script that uses Tor for anonymizing internet traffic. It sets up iptables and Tor to route all services and traffic, including DNS, through the Tor network.

## Author s3r4ph1

This script was written by Rupe (version 2.1).

## Installation and Usage

### 1. Install Python 3

Ensure Python 3 is installed on your system. You can check this with:

```bash
python3 --version


sudo apt update
sudo apt install python3
sudo apt install tor
sudo systrmctl start tor

chmod +x s3r4ph1.py

Run the Script
Load iptables rules:
sudo ./s3r4ph1.py --load

Flush iptables rules:
sudo ./s3r4ph1.py --flush

Get the current public IP address:
./s3r4ph1.py --ip

Refresh the circuit and get a new IP address:
sudo ./s3r4ph1.py --refresh




## Автор: s3r4ph1

### 1. Установите Python 3
s3r4ph1 — это скрипт на Python, который использует Tor для анонимизации интернет-трафика. Он настраивает iptables и Tor для маршрутизации всех сервисов и трафика, включая DNS, через сеть Tor.

Cкрипт работает с python3
для начала установите tor
sudo apt update
sudo apt-get install tor
sudo systemctl start tor
chmod +x s3r4ph1.py

5. Запустите скрипт с нужным правилом
python3 s3r4ph1.py

Вы можете запустить скрипт несколькими способами в зависимости от того, что вы хотите сделать:
Загрузить правила iptables
bash
sudo ./s3r4ph1.py --load
Сбросить правила iptables:
bash
sudo ./s3r4ph1.py --flush
Получить текущий публичный IP-адрес:
bash
./s3r4ph1.py --ip
Изменить цепочку и получить новый IP:
bash
sudo ./s3r4ph1.py --refresh
