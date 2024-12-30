
class GPIO:
    def __init__(self, com):
        self.TUP = 13.0
        self.TDOWN = 12.5
        self.led = PWM(Pin(15), freq=1000)
        self.ledValue = 0
        self.MHaut = Pin(2, Pin.OUT)
        self.MBas = Pin(4, Pin.OUT)
        self.Bp = Pin(16, Pin.IN, Pin.PULL_DOWN)
        self.OldBp = self.Bp.value()
        self.com = com

    async def ExecuteLoopLed(self):
        while True:
            msg = self.com.getMsgLed()
            if msg is not None:
                if msg <= 3:
                    self.led.duty(0)
                    self.ledValue = 0
                elif msg <= 100:
                    self.led.duty(msg * 10)
                    self.ledValue = msg
                    print("Led set to:", self.ledValue)

            if self.Bp.value() != self.OldBp and self.ledValue:
                self.com.sendMsg("500")
                await self.ChangeLed(0)
            elif self.Bp.value() != self.OldBp:
                self.com.sendMsg("501")
                await self.ChangeLed(100)
            self.OldBp = self.Bp.value()

            await asyncio.sleep(0.03)

    async def goDown(self):
        startTime = time()
        self.MHaut.value(0)
        self.MBas.value(1)
        while time() - startTime < self.TDOWN:
            if self.com.getMsgBlind() == 122:
                break
            await asyncio.sleep(0.5)
        self.MBas.value(0)

    async def goUp(self):
        startTime = time()
        self.MBas.value(0)
        self.MHaut.value(1)
        while time() - startTime < self.TUP:
            if self.com.getMsgBlind() == 122:
                break
            await asyncio.sleep(0.5)
        self.MHaut.value(0)

    async def ExecuteBlindLoop(self):
        while True:
            msg = self.com.getMsgBlind()
            if msg is not None:
                if msg == 122:
                    self.MHaut.value(0)
                    self.MBas.value(0)
                elif msg == 121:
                    self.MHaut.value(0)
                    self.MBas.value(1)
                    await asyncio.sleep(1)
                    self.MBas.value(0)
                elif msg == 123:
                    self.MBas.value(0)
                    self.MHaut.value(1)
                    await asyncio.sleep(1)
                    self.MHaut.value(0)
                elif msg == 120:
                    await self.goDown()
                elif msg == 124:
                    await self.goUp()

            await asyncio.sleep(0.05)


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


