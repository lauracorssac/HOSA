class SystemStatusManager(object):

    def get_last_status():
        with open("last_system_state", 'r') as f:
            line = f.readline().strip()
            value = float(line)
            return value

    def save_last_status(value):
        with open("last_system_state", 'w') as f:
            f.write(str(value))
