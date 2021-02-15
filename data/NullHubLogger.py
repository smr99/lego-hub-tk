from data.HubLogger import HubLogger

class NullHubLogger(HubLogger):
    def program_runstatus_update(self, timestamp, program_id, is_running):
        pass

    def telemetry_update(self, timestamp, message, hubstatus):
        pass