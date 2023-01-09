import threading
import time
from services.thundersynchandler import ThunderSyncHandler


class SettingsIntervalHandler:

    RUNNING = True

    def run(self, statusBadge):
        self.statusBadge = statusBadge
        t1 = threading.Thread(target=self.start)
        t1.start()

    def start(self):

        try:
            while SettingsIntervalHandler.RUNNING:
                status = "unknown"
                if ThunderSyncHandler.STATUS == 0:
                    status = "offline"
                if ThunderSyncHandler.STATUS == 1:
                    status = "waiting for changes"
                if ThunderSyncHandler.STATUS == 2:
                    status = "syncing"
                print("Status: " + status)
                self.statusBadge.setText("Status: " + status)
                time.sleep(1)
        except:
            print("ThunderSyncHandler Observer error")
