# Capturing a 4-Way Handshake from WPA/WPA2 WiFi Networks with a Python Script
A python script for capturing 4-way handshakes for WPA/WPA2 WiFi networks.

To crack passwords from the captured handshake data obtained by this script, see our other repo:
<a href="https://github.com/ZeroDayArcade/cracking-wpa-with-handshake">Cracking WPA/WPA2 WiFi Passwords from a Captured Handshake</a>

This script will produce hash lines in the hashcat hc22000 format that can be cracked with hashcat or with the script referenced above. It is built for simplicity and comprehension and is meant to help those looking to build their own hacking tools get started with a bare-bones example.

You will need a WiFi adapter capable of monitor mode. I tested this with three different adaptors including <a href="https://www.amazon.com/GenBasic-Wireless-Network-Dongle-Adapter/dp/B0BNFKJPXS/">this one for less than $10 on Amazon</a>. I recomend running this script on a Linux distribution, and have successfully tested it with Kali Linux on Intel and Raspian on a Raspberry Pi 4 (ARM). If you are running macOS or Windows, then you can use the script with a Virtual Machine running Kali or other distributions with VirtualBox or VMWare. 

*Only ever hack a network you own and have legal permission to hack. This is for educational purposes only.* 

## Setting up a test WiFi Network

`capture_handshake.py` will work with many common wireless routers as well as access points created with development boards like the ESP8266 NodeMCU. Depending on your exact setup you may have to tweak some variables in the script slightly, but I have tested it on several systems successfully.

One of the cheapest and easiest ways to practice WiFi hacking is with an ESP8266 NodeMCU development board. These boards can be picked up from Amazon and other sites for just a few dollars and there are a ton of online examples and tutorials for them. They are compatable with the Arduino IDE and can act as a soft Access Point with just a few lines of code. In other words, you can use them to create WiFi networks that you can then hack. This makes them ideal for anyone wanting to start practicing WiFi network penetration testing without breaking the bank. Here is a link to the <a href="https://www.amazon.com/KeeYees-Internet-Development-Wireless-Compatible/dp/B07HF44GBT/">exact ESP8266 NodeMCUs</a> I used to test this script with, only ~$5 per unit at the time of this writing. Larger packs can be as low as $2.50 a unit.

I've included an optional Arduino IDE compatable `ZDA_WiFi.ino` file with this project that you can upload to an ESP8266 NodeMCU to create a test WiFi network to practice with. It is set with SSID = `ZDA WiFi` and password = `12345678`. You can use it with the instructions below to practice capturing and cracking 4-way handshakes just like you would with a commercial wireless router. For instructions on compiling and uploading code to these boards with the Arduino IDE 2.0 see <a href="https://randomnerdtutorials.com/installing-esp8266-nodemcu-arduino-ide-2-0/">these instructions</a>, select board **NodeMCU 1.0 (ESP-12E Module)** in the Arduino IDE when compiling/uploading.

## Getting and running the script
Clone the project:
```
git clone https://github.com/ZeroDayArcade/capture-handshake-wpa-wifi-hacking.git
```
cd into project directory:
```
cd capture-handshake-wpa-wifi-hacking
```
Put your WiFi adapter into monitor mode. Let's say your WiFi interface is called `wlan1`:
```
sudo ifconfig wlan1 down
```
```
sudo iwconfig wlan1 mode monitor
```
```
sudo ifconfig wlan1 up
```
With a WiFi network setup up for penetration testing, you can run this script to capture a handshake and crack the resulting hash line to get the password of the network. Let's say you've set up a test WiFi network with SSID = `ZDA WiFi` and password = `12345678`. Before you run the script, verify that you can connect to the AP with the password `12345678` on a seperate device such as a phone or with the internal WiFi adapter of your computer (the one you're not using for monitor mode!). Once you've confirmed the AP is set up correctly and you can connect to it, disconnect your phone/extra device from the AP for the test. Then run `capture_handshake.py` and wait for a handshake with:
```
sudo python3 capture_handshake.py wlan1 "ZDA WiFi"
```
**Note:** this assumes there is only one network in range with that name. If more than one, you can specify the MAC address with:
```
sudo python3 capture_handshake.py wlan1 "ZDA WiFi" <MAC_ADDRESS_AP>
```
This will listen for devices connecting to `ZDA WiFi`. Reconnect to the network with your seperate device. When you do, the script will take packets/frames from the 4-way handshake and then print a hashcat hc22000 format hash line in Terminal once captured. The hash line will also be saved/create a file named hashline.txt containing the hash line from the captured handshake. You can then use that hash line with hashcat or our <a href="https://github.com/ZeroDayArcade/cracking-wpa-with-handshake">handshake cracking script</a> to crack the password of the network which should yield the `12345678` password in this example. Of course you can always have someone else set the password so you don't know what it is before hand, and then try to capture and crack a handshake from the network for the unknown password.

## Using a Half-Handshake vs. Full Handshake

The script will construct the hash line from the first 2 messages of the handshake. This is sufficient in most cases. Assuming the connecting device (phone/extra device in the example above) is connecting with the correct password, it will be possible to crack the resulting hash line to get the real password of the network. If the connecting device attempts to connect with the wrong password, the script will run normally but the hash line will obviously not contain the real password. 

You can easily modify the script to use the `mic` and `eapol_client` from the 4th message instead. If you want to use the data from the 4th message and still crack the handshake with `crack_handshake.py` and `passlist.txt` from the <a href="https://github.com/ZeroDayArcade/cracking-wpa-with-handshake">Cracking WPA/WPA2 WiFi Passwords from a Captured Handshake</a> repo, you'll need to pass in all the variables to `crack_handshake()` explicitly instead of using the hash line.

For example, if `crack_handshake.py` and `passlist.txt` are in the same directory as `capture_handshake.py`, you can add the following lines to `capture_handshake.py` under `elif message_num == 4 and data_from_cl:`
```
sys.argv = [sys.argv[0]]
import crack_handshake as ctools
eapol_client = b''.join([eapol_frame_before_mic, bytearray(16), wpa_length])
ctools.crack_handshake(mic, mac_ap, mac_cl, bytes(essid, 'utf-8'), nonce_ap, nonce_cl, eapol_client)
```
to capture *and* crack the handshake when you run `capture_handshake.py`.

You do this when cracking with message 4 data instead of running `crack_handshake.py` with a hash line because `crack_handshake.py` pulls `nonce_cl` from the `eapol_client` part of the hash line before running the cracking function. Doing this works when cracking with message 2 because `nonce_cl` is included in the `eapol_client` of message 2, but `nonce_cl` is not in the `eapol_client` of message 4 and thus `nonce_cl` must be passed in explicitly.
<br/>

# More Zero Day Arcade Tutorials:
**Learn Reverse Engineering, Assembly, Code Injection and More:**  
🎓  <a href="https://zerodayarcade.com/tutorials">zerodayarcade.com/tutorials</a> 

**More WiFi Hacking with Simple Python Scripts:**  
<a href="https://github.com/ZeroDayArcade/capture-pmkid-wpa-wifi-hacking">Capturing PMKID from WiFi Networks</a>  
<a href="https://github.com/ZeroDayArcade/wpa-password-cracking-with-pmkid">Cracking WiFi Passwords with PMKID</a>   
<a href="https://github.com/ZeroDayArcade/cracking-wpa-with-handshake">Cracking WPA/WPA2 Passwords with 4-Way Handshake</a>  

# Find Hacking Bounties in Gaming:
🎮  <a href="https://zerodayarcade.com/bounties">zerodayarcade.com/bounties</a>






