from communication import Communication
from gpio import GPIO


async def main():
    try:
        com = Communication()
        print("Com OK")
    except:
        print("NO COM")
        await offlineLed()
    gpio = GPIO(com)
    print("GPIO READY")
    await asyncio.gather(
        gpio.ExecuteLoopLed(),
        gpio.ExecuteBlindLoop()
    )

# Lancer le programme principal
asyncio.run(main())