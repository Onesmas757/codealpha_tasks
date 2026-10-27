from scapy.all import sniff

packets = sniff(iface="wlo1", filter="icmp", count=1)
packets[0].show()
