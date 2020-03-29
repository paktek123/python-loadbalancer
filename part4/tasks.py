from models import Server
import sys
import time

def background_healthcheck(register, interval):
    while True:
        time.sleep(interval)
        for host in register:
            for server in register[host]:
                server.healthcheck_and_update_status()
        print(register, file=sys.stdout)
            
