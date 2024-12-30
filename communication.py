
import time
import uasyncio as asyncio
import network

SSID = "Home"
PWD = "a1b2c3d4"

class Communication:
    def __init__(self, gpio):
        self.ap_ssid = "ESP-POUTRE"
        self.ap_pwd = "0123456789"
        self.gpio = gpio
        self.messageLed = None
        self.messageBlind = None
        self.ConnectWifi()
        asyncio.run(self.main())

    def ConnectWifi(self):
        
        self.wlan.active(True)
        self.wlan.connect(SSID, PWD)
        start = time.time()
        while self.wlan.isconnected() == False and time.time() - start <= 15:
            pass
        if not self.wlan.isconnected():
            self.setup_ap()
        print("Adresse IP:", self.wlan.ifconfig()[0])
    
    def setup_ap(self):
        self.wlan.config(essid=self.ssid, password=self.password)
        self.wlan.active(True)
        print("Point d'accès activé avec SSID:", self.ssid)


    async def ReconnectWifi(self):
        self.wlan.connect(SSID, PWD)
        while self.wlan.isconnected() == False and time.time() - start <= 15:
            pass
        if not self.wlan.isconnected():
            self.setup_ap()

    
    async def readMsg(self):
        while True:
            message = await self.mqtt.wait_msg()
            if int(message) <= 110:
                self.messageLed = int(message)
            else:
                self.messageBlind = int(message)

    def getMsgLed(self):
        msg = self.messageLed
        self.messageLed = None
        return msg
    
    def getMsgBlind(self):
        msg = self.messageBlind
        self.messageBlind = None
        return msg

    async def sendMsg(self, msg):
        await self.mqtt.publish(TOPIC, msg)
    


        

    async def get_html(self):
        html1 = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
            </head>
            <body>
                <title>ESP32-Poutre</title>
                <style>

                    body{
                        background-color: #252525;
                        color: rgb(205, 200, 200);
                        font-size: 50px;
                        text-align: center;
                    }
                    input[type="submit"] {
                        height: 50px;
                        border-radius: 8px;
                        font-size: 40px;
                    }
                    button {
                        height: 60px;
                        border-radius: 8px;
                        font-size: 40px;
                    }
                </style>
        """
        html1 += """
            <h1>Light settings</h1>
            <form action="/up" method="GET">
                <button type="submit">Blind up</button>
                    </form>
                    <form action="/up_small" method="GET">
                        <button type="submit">Blind small up</button>
                    </form>
                    <form action="/dwn" method="GET">
                        <button type="submit">Blind down</button>
                    </form>
                    <form action="/dwn_small" method="GET">
                        <button type="submit">Blind small down</button>
                    </form>
                    <br>
                    <label for="light">Light </label><input type="range" id="slider" name="value" min="0" max="100" step="1" value="{ledValue}" oninput="sendSliderValue()" /><br>
        """
        #.format(ledValue=self.gpio.ledValue)
   
        html1 += """    <script>
        // Fonction qui envoie la valeur du slider via une requête GET en temps réel
        function sendSliderValue() {
            var sliderValue = document.getElementById("slider").value;
            // Utilisation de fetch pour envoyer la requête GET en temps réel
            fetch("/light/" + sliderValue)
            .then(response => response.text())  // Pour traiter la réponse du serveur si nécessaire
            .then(data => {
                console.log("Réponse reçue du serveur:", data);
            })
            .catch(error => {
                console.error("Erreur lors de l'envoi de la requête:", error);
            });
        }
        </script>
            </body>
            </html>"""
        return html1



    async def html_result(self, title, content):
        html1 = """
                <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
            </head>
            <body>
                <title>ESP32 Settings</title>
                <style>

                    body{
                        background-color: #252525;
                        color: rgb(205, 200, 200);
                        font-size: 40px;
                        text-align: center;
                    }
                </style>
        """
        html1 += "<h1>" + title + "</h1><br>"
        html1 += content
        html1 += "</body></html>"
        return html1

    async def handle_client(self, reader, writer):
        try:
            # Lire la requête HTTP
            request = await reader.read(1024)
            request_str = request.decode()
            code = 200
            print("<-------------------- BODY -------------------->")
            print(request_str)
            print("<-------------------- BODY -------------------->")
            # Vérifier si c'est une requête GET pour afficher le formulaire
            if request_str.startswith('GET /'):
                response_body = await self.get_html()
            if request_str.startswith("GET /light/"):
                line = string.splitlines()[0]
                value_str = line.split("/")[2]
                value_int = value_str.split(" ")[0]
                # TODO ADD CHANGE LIGHT
            elif request_str.startswith("GET /up HTPP/1.1"):
                pass #TODO
            elif request_str.startswith("GET /up_small HTPP/1.1"):
                pass #TODO
            elif request_str.startswith("GET /dwn HTPP/1.1"):
                pass #TODO
            elif request_str.startswith("GET /dwn_small HTPP/1.1"):
                pass #TODO
            else:
                code = 404
                response_body = await self.html_result("Error 404", "Page not found")

            header = f"HTTP/1.1 {code} OK\r\nContent-Type: text/html\r\n\r\n"
            writer.write(header.encode())
            writer.write(response_body.encode())
            await writer.drain()

        except Exception as e:
            print("Erreur lors de la gestion du client:", e)
        finally:
            await writer.aclose()
            
    async def start_web_server(self):
        server = await asyncio.start_server(self.handle_client, '0.0.0.0', 80)
        print("Serveur Web démarré sur le port 80")
        
        async with server:
            while True:
                await asyncio.sleep(1) 

        print("Serveur arrêté.")

    async def main(self):
        await self.start_web_server()


Communication(None)