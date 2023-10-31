# Setup

## Set environment variables on host

Um dauerhafte Umgebungsvariablen unter Ubuntu zu erstellen, die nach einem Neustart weiterhin verfügbar sind.

1. Öffnen Sie ein Terminal.

2. Um ".bashrc" zu bearbeiten, geben Sie den folgenden Befehl im Terminal ein und drücken Sie Enter:

    ```bash
    vim ~/.bashrc
    ```

4. Am Ende der Datei können die Umgebungsvariablen hinzufügen. 

    ```bash
    export MEROSS_EMAIL="test@test.com"
    export MEROSS_PASSWORD="pass"
    export TELEGRAM_TOKEN="pass"
    ```

5. Damit die Änderungen wirksam werden, laden Sie Ihre Umgebungsvariablen neu, indem Sie den folgenden Befehl eingeben:

    ```bash
    source ~/.bashrc
    ```



## Install requirements 

```bash
pip install -r requirements.txt
```


## Set up daemon on host

Um einen Daemon unter Ubuntu zu erstellen, der alle 5 Minuten einen bestimmten Code ausführt, kannst du die folgenden Schritte befolgen:


1. **Bash-Skript erstellen**: 

    Erstelle ein Bash-Skript, das deinen Code ausführt:

   ```bash
   #!/bin/bash
    while true; do
        python3 /home/pi/code/plug-control/plug-control.py
        sleep 300
    done
   ```

   

2. **Skript ausführbar machen**: 

    Mache dein Bash-Skript ausführbar:

   ```bash
   chmod +x plug-daemon.sh
   ```

3. **Daemon erstellen**: 

    Du kannst das `systemd`-Tool verwenden, um deinen Daemon zu erstellen. Erstelle eine `.service`-Datei, z.B. `mein_daemon.service`, im Verzeichnis `/etc/systemd/system/` und öffne sie in einem Texteditor:

   ```bash
   sudo vim /etc/systemd/system/plug-daemon.service
   ```

   Füge folgenden Inhalt ein und update die Environment varables mit dem secrets

   ```plaintext
    [Unit]
    Description=Plug Daemon
    After=network.target

    [Service]
    Type=simple
    User=pi
    Group=pi
    Environment=MEROSS_EMAIL="mail@mail.com"
    Environment=MEROSS_PASSWORD="pass"
    Environment=TELEGRAM_TOKEN="pass"
    ExecStart=/home/pi/code/plug-control/plug-daemon.sh

    [Install]
    WantedBy=multi-user.target
   ```


4. **Systemd-Dienst aktivieren und starten**:

   ```bash
   sudo systemctl enable plug-daemon.service
   sudo systemctl start plug-daemon.service
   ```

5. **Überprüfen, ob der Daemon läuft**:

   ```bash
   sudo systemctl status plug-daemon.service
   ```


Jetzt wird dein Daemon alle 5 Minuten den Code ausführen. Du kannst die Aktivität und Protokolle des Daemons mithilfe des `systemctl`-Befehls überwachen. Beachte, dass du den Pfad zu deinem Code und deinem Bash-Skript entsprechend anpassen musst.



