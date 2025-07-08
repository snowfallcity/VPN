#!/bin/bash

apt update
apt install -y wireguard iptables

mkdir -p /etc/wireguard
cd /etc/wireguard

# Generate keys for server
umask 077
wg genkey | tee server_private.key | wg pubkey > server_public.key

S_PRIVATE_KEY=$(cat server_private.key)
S_PUBLIC_KEY=$(cat server_public.key)

# Client Setup
C_PUBLIC_KEY="__placeholderForClientPublicKey__"
C_IP="10.0.0.2"

cat > wg0.conf <<EOF
[Interface]
PrivateKey = \$S_PRIVATE_KEY
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = \$C_PUBLIC_KEY
AllowedIPs = \$C_IP/32
EOF

# Enable IP forwarding
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
sysctl -p

# Bring up interface
wg-quick up wg0
systemctl enable wg-quick@wg0