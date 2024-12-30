from communication import Communication
from gpio import GPIO
import uasyncio as asyncio




async def main():
    try:
        com = Communication()
        print("Com OK")
    except:
        print("NO COM")
    gpio = GPIO(com)
    com.gpio = gpio
    print("GPIO READY")
    await asyncio.gather(
        gpio.ExecuteLoopLed(),
        com.main(),
    )

# Lancer le programme principal
asyncio.run(main())