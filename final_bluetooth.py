import machine
#from machine import Pin
from machine import Timer
from time import sleep_ms
import ubluetooth
from machine import Pin, SPI, SoftSPI
import sdcard
import os
import json
uart = machine.UART(2, 115200)
# Initialize the SD card
spi=SoftSPI(1,sck=Pin(18),mosi=Pin(23),miso=Pin(19))
sd=sdcard.SDCard(spi,Pin(05))
message = ""
vfs=os.VfsFat(sd)
 
# Mount the SD card
os.mount(sd,'/sd')

# Debug print SD card directory and files
print(os.listdir('/sd'))

class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):        
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global message
        
        if event == 1: #_IRQ_CENTRAL_CONNECT:
                       # A central has connected to this peripheral
            self.connected()

        elif event == 2: #_IRQ_CENTRAL_DISCONNECT:
                         # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()
        
        elif event == 3: #_IRQ_GATTS_WRITE:
                         # A client has written to this characteristic or descriptor.          
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode('UTF-8').strip()
            print(message)
            
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")
ble = ESP32_BLE("ESP32BLE")        
while True:
	# if there is character in receive serial buffer
    strMsg =0
    if uart.any() > 0:
    	# Read all the character to strMsg variable
        strMsg = uart.read()
        # Debug print to REPL
        print(strMsg)
        strMsg=str(strMsg)
        #data = "20230203@9:23PM@coffee"
        newd = strMsg.split('@')
        #data = "20230203@9:23PM@coffee"
        #newd = data.split('@')
        vdate = newd[1]
        vdrinks = newd[2]
        a1 = "date"
        b1 = "drinks"
        print(vdrinks)
        print(vdate)
        newdata = "{" + '"' + a1 + '"' + ":" + " " + vdate + ',' + '"' + b1 + '"' + ":" + " " + '"' + vdrinks + '"' + "}"
        
        #newdata = str(newdata)
        print(newdata)
        #hel = newdata
        jsodata = json.loads(newdata)
        #print(jsodata)
        filename = '/sd/your_file.json'
        entry = jsodata
        #entry = {"drinks": "hot_juice", "date": 20011212}
        #print(entry)
        with open(filename, "r") as file:
            data = json.load(file)

# 2. Update json object
        data.append(entry)

    # 3. Write json file
        with open(filename, "w") as file:
            json.dump(data, file)
#             print(data)
            print(len(data))

        file.close()
        #@20220206@coffee@ @22020207@tea@ @20220206@blacktea@
#bluetooth section//////////////////////////////////        
    if message > '0': 
        #print(message)
        #message = ""
        newd = str(message)
        newd = newd.split('@')
        startdate = newd[1]
        enddate = newd[2]
        print("start data is :" +startdate)
        print("enda data is :" +enddate)
        print(type(startdate))
        finalstartdate = int(startdate)
        print(type(finalstartdate))
        finalenddate = int(enddate)
        print(type(finalenddate))
        #exy = 20220211
        #print(type(exy))
        filename = '/sd/your_file.json'
        with open(filename, 'r', encoding='utf-8') as f:
                      a_list = json.load(f)

                      #print(a_list)
                      print(len(a_list))
#         with open(filename, "r") as file:
#             data = json.load(file)
            #print(data)
        filtered_list = [
        dictionary for dictionary in a_list if dictionary['date'] <= finalenddate]

          
        #print(filtered_list)
        print(len(filtered_list))

        new_filter = [ dictionary for dictionary in filtered_list if dictionary['date'] >= finalstartdate
          ]
         
        #print(new_filter)
        print(len(new_filter))
        
        coffee_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "coffee"
          ]
         
        #print(coffee_filter)
        print("no of coffee:")
        print(len(coffee_filter))
        
        strongcoffee_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "strongcoffee"
          ]
         
        #print(coffee_filter)
        print("no of strongcoffee:")
        print(len(strongcoffee_filter))
        
        blackcoffee_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "blackcoffee"
          ]
         
        #print(coffee_filter)
        print("no of blackcoffee:")
        print(len(blackcoffee_filter))
        
        
        tea_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "tea"
          ]
         
        #print(tea_filter)
        print("no of tea:")
        print(len(tea_filter))
        
        strongtea_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "strongtea"
          ]
         
        #print(tea_filter)
        print("no of strongtea:")
        print(len(strongtea_filter))
        
        
        blacktea_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "blacktea"
          ]
         
        #print(tea_filter)h
        print("no of blacktea:")
        print(len(blacktea_filter))
        
        hotwater_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "hotwater"
          ]
         
        #print(tea_filter)
        print("no of hotwater:")
        print(len(hotwater_filter))
        
        milk_filter = [ dictionary for dictionary in new_filter if dictionary['drinks'] == "milk"
          ]
         
        #print(tea_filter)
        print("no of milk:")
        print(len(milk_filter))
        ble.send(str(len(coffee_filter)) +"@" +str(len(strongcoffee_filter)) +"@" +str(len(blackcoffee_filter)) +"@" +str(len(tea_filter)) +"@" +str(len(strongtea_filter)) +"@" +str(len(blacktea_filter))  +"@" +str(len(hotwater_filter)) +"@" +str(len(milk_filter)))
        message = ""
        
               