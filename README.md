![alt text](https://github.com/Neelov12/Diablo/blob/320d44b089b116f223bdac13da280cc1e830e923/logo.png "logo")

# Diablo VPN 
## About
**Diablo VPN** is an open-source, local network VPN service meant to protect your traffic on a home or business network. 

> *"Wait, a local network VPN? What's the point of that?"*

Well, you might be surprised how easy it is for hackers to infiltrate and spy on your local network. For most router set ups, a couple of ARP requests from a malicious device is all it takes to spoof your device's identity. This means just about anyone with the motivation can act as a man in the middle between you and the internet (and that's just the start). 

Diablo VPN addresses this by allowing users to self-host a VPN server on their local network, allowing trusted clients to securely connect, encrypt, and reroute their traffic through the server. Additionally, the server acts as a manager of sorts for clients, dropping any ARP requests that come their way. This allows clients completely disappear from the POV of an outside observer. 

## Features 
Diablo VPN hosts a variety of unique protective features for the local network:\

> 🛡️  **Client invisibility**:   Using firewall + TUN isolation + no ARP replies\
🔐 **Encrypted comms (TLS)**:   All traffic between client and proxy is encrypted over TCP\
🔍 **Protection from LAN MITM attacks**: Since clients talk only to proxy, attackers can't hijack DNS/HTTP\
🧅 **Hidden from LAN scans**:   ARP blocking, TUN-only IP, port filters make the client invisible\
🧻 **Rogue DHCP/DNS/ARP**:      Firewall rules to block ports 53 (DNS), 67/68 (DHCP), and ARP replies\
🔁 **Proxy ARP response**:      Proxy pretends to be clients when needed\
🧱 **Firewalling LAN traffic**: Options to firewall custom traffic\

## Installation 
### Quick Install (Recommended)
```bash
pipx install git+https://github.com/Neelov12/Diablo
```
### Or with virtualenv: 
```bash
git clone https://github.com/Neelov12/Diablo.git
cd Diablo
python3 -m venv venv
source venv/bin/activate
pip install .
```
### Reinstalling in virtualenv: 
```bash
source venv/bin/activate
pip install --force-reinstall .
```
### Developer mode: 
```bash
pip install --editable
```
### If requirements did not install automatically:
```bash
pip install -r requirements.txt
```

## Version Beta 1.3 
Diablo VPN is currently in it's early stages of deployment. Continued updates and improvements are to be expected. 

## Contact 
If you have any inquiries, or are interested in becoming a developer, I can be reached at neelov12@gmail.com.
