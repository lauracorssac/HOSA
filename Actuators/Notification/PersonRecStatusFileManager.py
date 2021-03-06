

class PersonRecStatusFileManager(object):

    def save_last_person_rec_status(last_status):
        f = open("person_rec_status.txt", "w")
        f.write(str(last_status))
        f.close()

    def get_last_person_rec_status():
        with open('person_rec_status.txt', 'r') as f:
            line = f.readline()
            line = line.strip()
            if float(line) == 1 or float(line) == 0:
                return float(line)
            else:
                return -1.0
        return -1.0
