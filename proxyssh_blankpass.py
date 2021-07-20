# To run this program, the file ``ssh_host_key`` must exist with an SSH
# private key in it to use as a server host key. An SSH host certificate
# can optionally be provided in the file ``ssh_host_key-cert.pub``.

import asyncio, asyncssh, crypt, sys, logging, random, paramiko

async def process_line(line, process, client, command=False):

    log_client = f'USER: {process._conn._username} ADDR: {process._conn._peer_addr} PORT: {process._conn._peer_port} CLIENT COMMAND: {line}'
    logging.info(log_client)
    print(log_client)
    stdin, stdout, stderr = client.exec_command(line)
    if command:
        result = stdout.read().decode("utf-8")
    else:
        result = stdout.read().decode("utf-8") + "[admin@MikroTik] > "
    log_server = f'USER: {process._conn._username} ADDR: {process._conn._peer_addr} PORT: {process._conn._peer_port} SERVER RESPONSE:\n{result}'
    logging.info(log_server)
    print(log_server)
    process.stdout.write(result)

async def handle_client(process):

    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect('172.16.255.100', username='admin', password='')
    process.stdout.write("[admin@MikroTik] > ")

    if process.command:
        print("SSH COMMAND RECEIVED")
        await process_line(process.command, process, client, command=True)
    else:
        try:
            async for line in process.stdin:
                line = line.rstrip('\n')
                await process_line(line, process, client)
                if line.lower().strip() == 'quit':
                    break
        except asyncssh.BreakReceived:
            pass

    client.close()
    process.exit(0)

class MySSHServer(asyncssh.SSHServer):

    def connection_made(self, conn):
        """Handle a newly opened connection"""

        conn._version = b'ROSSSH'
    
    def connection_lost(self, exc):
        if exc:
            print('SSH connection error: ' + str(exc), file=sys.stderr)
        else:
            print('SSH connection closed.')

    def begin_auth(self, username):
        # If the user's password is the empty string, no auth is required
        logging.info(username)
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        logging.info(f'USER: {username} PASS: {password}')
        if password == '':
            return True
        else:
            print('not a blank password')
            return False

async def start_server():
    await asyncssh.create_server(MySSHServer, '', 8022,
                                 server_host_keys=['honey_key'],
                                 process_factory=handle_client)

logging.basicConfig(filename='proxyssh_2.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()
