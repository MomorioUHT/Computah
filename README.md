## Computah

---

<img src="https://i.ibb.co/fSCQtGf/Penguin.png" alt="Penguin" border="0">

Based on "Bhan Rhan COM" discord, this toaster has been playing the music for a while

---

Please use carefully with your bot

Requirements 
```
discord
yt-dlp (Should always be the latest one :P)
python-dotenv <- You can hard code the token here if you too lazy
```

FFMpeg
https://www.ffmpeg.org/download.html (self host)

Build the docker image
```
docker build -t . <img-name>
```

Deploy using the command
```
docker run --name <your-container-0> -e TOKEN=yourtokenblyat <img-name>
```

คนที่มาอ่านมันคง Deploy docker เป็นอยู่แล้วมะ?! \
จะไม่ใช้ docker ก็ได้ แล้วแต่ ตามใจ

---
