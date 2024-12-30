import time
import uasyncio as asyncio
import network
import urequests as requests


SSID = "Home"
PWD = "a1b2c3d4"
RPI = "http://192.168.1.200:1880/poutre"


class Communication:
    def __init__(self):
        self.ap_ssid = "ESP-POUTRE"
        self.ap_pwd = "0123456789"
        self.gpio = None
        self.messageLed = 100
        self.wlan = network.WLAN(network.STA_IF)
        self.ConnectWifi()
        
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
                
    def getMsgLed(self):
        msg = self.messageLed
        self.messageLed = None
        return msg
    
    def sendMsg(self, path):
        print("SENDING MSG :", path)
        try:
            response = requests.get(RPI + path)
        except Exception as e:
            print("Request fail :", RPI, "\n",e)
            return 500
        tmp = response.status_code
        print(response.text)
        response.close()
        return tmp


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
            
            if request_str.startswith("GET /light/"):
                line = request_str.splitlines()[0]
                value_str = line.split("/")[2]
                value_int = int(value_str.split(" ")[0])
                self.messageLed = value_int
                response_body = await self.get_html()
            elif request_str.startswith('GET /'):
                response_body = await self.get_html()
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

#Communication(None)