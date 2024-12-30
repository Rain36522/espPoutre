from machine import Pin, PWM
import uasyncio as asyncio


class GPIO:
    def __init__(self, com):
        self.led = PWM(Pin(4), freq=1000)
        self.ledValue = 0
        self.Bp = Pin(2, Pin.IN, Pin.PULL_DOWN)
        self.OldBp = self.Bp.value()
        self.com = com

    async def ExecuteLoopLed(self):
        while True:
            msg = self.com.getMsgLed()
            if msg is not None:
                print("MSG :", msg)
                if msg <= 3:
                    self.led.duty(0)
                    self.ledValue = 0
                elif msg < 100:
                    self.led.duty(msg * 10)
                    self.ledValue = msg
                    print("Led set to:", self.ledValue)
                elif msg == 100:
                    self.led.duty(1023)
                    self.ledValue = msg
            print("LED VALUE :", self.ledValue)
            if self.Bp.value() != self.OldBp and self.ledValue:
                self.com.sendMsg("/off")
                await self.ChangeLed(0)
            elif self.Bp.value() != self.OldBp:
                self.com.sendMsg("/on")
                await self.ChangeLed(100)
            self.OldBp = self.Bp.value()

            await asyncio.sleep(0.03)


    async def ChangeLed(self, value):
        while self.ledValue != value:
            change = 1 if self.ledValue <= 10 else self.ledValue // 10
            if change >= abs(self.ledValue - value):
                self.ledValue = value
            elif self.ledValue < value:
                self.ledValue += change
            else:
                self.ledValue -= change
            self.led.duty(self.ledValue * 10)
            await asyncio.sleep(0.02)


