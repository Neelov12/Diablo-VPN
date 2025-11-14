![alt text](https://github.com/Neelov12/Diablo/blob/320d44b089b116f223bdac13da280cc1e830e923/logo.png "logo")

# Diablo VPN 

Quick Install (Recommended)
```bash

pipx install git+https://github.com/Neelov12/Diablo

Or with virtualenv: 

git clone https://github.com/Neelov12/Diablo.git
cd Diablo
python3 -m venv venv
source venv/bin/activate
pip install .

Reinstall in virtualenv: 
source venv/bin/activate
pip install --force-reinstall .

Dev mode: 
pip install --editable

Goal    Feasibility over LAN with Router    Notes
🔐 Encrypted comms (TLS)    ✅ Fully supported  All traffic between client and proxy is encrypted over TCP (e.g., port 4433)
🛡️ Client invisibility  ✅ Achievable   Using firewall + TUN isolation + no ARP replies
🔍 Protection from LAN MITM attacks ✅ Very effective   Since clients talk only to proxy, attackers can't hijack DNS/HTTP
🔌 Wi-Fi vs Ethernet    ✅ Irrelevant to design All devices share the same broadcast domain; switch/router just forwards
🧅 Hidden from LAN scans    ✅ With proper client-side config   ARP blocking, TUN-only IP, port filters make the client invisible
🧻 Rogue DHCP/DNS/ARP attack defense    ✅ With added client rules  We'll write firewall rules to block ports 53 (DNS), 67/68 (DHCP), and ARP replies
🔁 Proxy ARP response   ✅ Works via spoofing ARP replies   Proxy pretends to be clients when needed
🧱 Firewalling LAN traffic on clients   ✅ Cross-platform achievable    Windows/macOS/Linux all allow LAN blocking with ufw, pf, or netsh

If requirements did not install automatically:
pip install -r requirements.txt
