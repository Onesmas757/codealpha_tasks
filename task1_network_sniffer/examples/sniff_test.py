from scapy.all import sniff

def show(packet):
    print(packet.summary())

sniff(iface="wlo1", filter="icmp", prn=show, count=8)
