# kodzu_thon

Telethon implementarion

## Installing

### 1. Environments

Set environment variables for API keys:

* `TELETHON_CITY` (name of your city)

* `TELETHON_API_HASH` (get [api_hash](https://my.telegram.org/auth?to=apps), under API Development)

* `TELETHON_API_ID`

in system environment for simple run, or in `.env` file for docker-compose using.

### 2. Docker compose
```
docker-compose up -d
```
### OR
### 2.Python

1. `pip install -r requirements.txt`

2. Install **ffmpeg** and **ffprobe**

    * [windows](https://ffmpeg.zeranoe.com/builds/) install and place `ffmpeg.exe`, `ffprobe.exe` in **PATH**
    * [linux](https://www.tecmint.com/install-ffmpeg-in-linux/) (just install, it will work)

3. Also You can use `telethon.service` template to install it as systemctl daemon