def healthcheck(register):
    for host in register:
        for server in register[host]:
            server.healthcheck_and_update_status()
    return register
