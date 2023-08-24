# Capturing a 4-Way Handshake from WPA/WPA2 WiFi Networks with a Python Script
A python script for capturing 4-way handshakes for WPA/WPA2 WiFi networks.

To crack passwords from the captured handshake obtained by this script, see our other repo:
<a href="https://github.com/ZeroDayArcade/cracking-wpa-with-handshake">Cracking WPA/WPA2 WiFi Passwords from a Captured Handshake</a>

This script will produce hash lines in the hashcat hc22000 format that can be cracked with hashcat or with the script referenced above. It is built for simplicity and comprehension and is meant to help those looking to build their own hacking tools get started with a bare-bones example.

Also, and I hope this goes without saying, only ever hack a network you own and have legal permission to hack. This is for educational purposes only and to help you advance your penetration testing skills and knowledge. 

One of the cheapest and easiest ways to practice WiFi hacking is with an ESP8266 NodeMCU development board. These boards can be picked up from Amazon and other sites for just a few dollars and there are a ton of online examples and tutorials for them. They are compatable with the Arduino IDE and can act as a soft Access Point with just a few lines of code. In other words, you can use them to create WiFi networks that you can then hack. This makes them ideal for anyone wanting to start practicing penetration testing without breaking the bank. This script will work with ESP8266 WiFi networks as well as those from common commercial routers. Depending on your exact setup you may have to tweek some variables in the script slightly, but I have tested it on several systems successfully.

You will need a WiFi adapter capable of monitor mode. I tested this with three different adaptors including <a href="https://www.amazon.com/GenBasic-Wireless-Network-Dongle-Adapter/dp/B0BNFKJPXS/">this one for less than $10 on Amazon</a>. I recomend running this script on a Linux distribution, and have successfully tested it with Kali Linux on Intel and Raspian on a Raspberry Pi 4 (ARM). If you are running macOS or Windows, then you can use the script with a Virtual Machine running Kali or other distributions with VirtualBox or VMWare. 

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
With a WiFi network setup up for penetration testing, you can run this script to capture a handshake and crack the resulting hash line to get the password of the network. Let's say you've set up a test WiFi network with SSID = `ZDA WiFi` and password = `12345678` on your test router or ESP8266 NodeMCU access point (and have WiFi interface `wlan1` for your WiFi adapter). You can run this script and wait for a handshake with:
```
sudo python3 capture_handshake.py wlan1 "ZDA WiFi"
```
**Note:** this assumes there is only one network in range with that name. If more than one, you can specify the MAC address with:
```
sudo python3 capture_handshake.py wlan1 "ZDA WiFi" <MAC_ADDRESS_AP>
```
This will listen for devices connecting to `ZDA WiFi`. To test it, connect to the network with the known password `12345678` on a seperate device or WiFi interface like your phone or your computer's built in WiFi interface. When you do, the script will take packets/frames from the 4-way handshake and then print a hashcat hc22000 format hash line in Terminal once captured. The hash line will also be saved/create a file named hashline.txt containing the hash line from the captured handshake. You can then use that hash line with hashcat or our <a href="https://github.com/ZeroDayArcade/cracking-wpa-with-handshake">handshake cracking script</a> to crack the password of the network which should yield the `12345678` password in this example. Of course you can always have someone else set the password so you don't know what it is before hand, and then try to capture and crack a handshake from the network for the unknown password.

<br/>

# More Zero Day Arcade Tutorials:
🎓  <a href="https://zerodayarcade.com/tutorials">zerodayarcade.com/tutorials</a> 

# Find Hacking Bounties in Gaming:
🎮  <a href="https://zerodayarcade.com/bounties">zerodayarcade.com/bounties</a>






