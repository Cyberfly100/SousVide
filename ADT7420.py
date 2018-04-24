import time
from Adafruit_I2C import Adafruit_I2C


class ADT7420:
	def __init__(self, I2C_ADDR=0x48):
		try:
			self.i2c = Adafruit_I2C(I2C_ADDR)
		except:
			print("Could not find device")
		
		self._DEBUG = True

		self._TMSB = 0x00
		self._TLSB = 0x01
		self._STAT = 0x02
		self._CONF = 0x03
		self._THIGHMSB = 0x04
		self._THIGHLSB = 0x05
		self._TLOWMSB = 0x06
		self._TLOWLSB = 0x07
		self._TCRITMSB = 0x08
		self._TCRITLSB = 0x09
		self._THYST = 0x0A
		self._ID = 0x0B
		self._RESET = 0x2F

		#set device to 16bit mode
		self.i2c.write8(self._CONF, 0b10000000)

	def get(self):
		CommErr = False
		try:
			[TMSB, TLSB] = self.i2c.readList(self._TMSB,2)
			Traw = TMSB*255+TLSB
		except:
			CommErr = True
			TMSB, TLSB, Traw = 0, 0, 0
		if TMSB>>7 == 1:
			T = (Traw-65536)/128.0 #Minus detected
		else:
			T = Traw/128.0
		return T, CommErr
		
if __name__ == "__main__":
	t = ADT7420()
	while True:
		time.sleep(0.05)
		T, err = t.get()
		print str(round(T,2))+" C"
		
