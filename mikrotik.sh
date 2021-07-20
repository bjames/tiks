#!/bin/bash
ports=(
	22
	21781
)

path="/media/bjames/data/logs/"

while true
do

echo "" > ${path}.mikrotikbrief.tmp
for i in ${!ports[@]}
do

	pass="tok"
	ip="172.16.255.$((100+$i))"

	echo "SSH to mikrotik$i on $ip ${ports[$i]}"
	sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -p ${ports[$i]} tik@$ip "log print" | grep "admin" >> ${path}mikrotik${i}_admin 
	sort -u -o "${path}mikrotik${i}_admin"  "${path}mikrotik${i}_admin"
	sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -p ${ports[$i]} tik@$ip "interface l2tp-client monitor numbers=0 once" > ${path}mikrotik${i}_l2tp
	echo "######### system history print" > ${path}mikrotik${i}
	sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -p ${ports[$i]} tik@$ip "system history print" >> ${path}mikrotik${i}
	echo "######### config export" >> ${path}mikrotik${i}
	sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -p ${ports[$i]} tik@$ip "export" | grep -v "#" >> ${path}mikrotik${i}
	echo "######### file print detail" >> ${path}mikrotik${i}
	sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -p ${ports[$i]} tik@$ip "file print detail" >> ${path}mikrotik${i}
	echo "######### socks connections" > ${path}mikrotik${i}_socks
	sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -p ${ports[$i]} tik@$ip "ip socks connections print" >> ${path}mikrotik${i}_socks

	if [[ $? -ne 0 ]]; then
		echo "SSH failed, performing discovery"
		ports[$i]=$(nmap $ip -p10000-40000 | grep tcp | grep -o [0-9]*)
		if [ -z "${ports[$i]}" ]; then
			echo "Discovery failed, defaulting to 22"
			ports[$i]=22
		fi
		echo "SSH Port changed to ${ports[$i]} for mikrotik$i $ip"
	fi
	echo "mikrotik$i ${ports[$i]}" >> ${path}.mikrotikbrief.tmp
done

mv ${path}.mikrotikbrief.tmp ${path}mikrotikbrief

echo "committing changes to git repo"
git -C ${path} add .
git -C ${path} stage .
git -C ${path} commit -m "tick"

echo "Sleep for 1 second"
sleep 1

done

exit 0
