""" Parses needed information from report collected by FFLogsApi

FFLogs AI data pipeline only needs 
"""

from fflogsapi import FFLogsClient

_CAST_EVENT_TYPE_NAME = 'cast'

class FflogsReportParser:
    def __init__(self, username, key):
        self.client = FFLogsClient(username, key)
    
    def __fetch_report__(self, report_key: str):
        return self.client.get_report(report_key)

    def __create_player_id_to_job_mapping(self, player_details):
        return {player_detail.id: player_detail.job for player_detail in player_details} 

    def __collect_only_cast_events(self, fight_events):
        return (report_event for report_event in fight_events if report_event['type'] == _CAST_EVENT_TYPE_NAME)
    
    def parse_report(self, report_key: str):
        """
        Args: report_key: key url of the report
            ex) If report url is https://www.fflogs.com/reports/41ry2hjTYvFLwJxA, report_key is '41ry2hjTYvFLwJxA'
   
        Returns:
            Parsed result data containing:
                * Dictionary mapping player id to the player's job
                * 'cast' events of the fight
        """
        report = self.__fetch_report__(report_key)
        kill_fights = [fight for fight in report.fights if fight.is_kill and fight.standard_comp] 
        player_id_job_mapping = self.__create_player_id_to_job_mapping(report.player_details())

        cast_events = [self.__collect_only_cast_events(kill_fight) for kill_fight in kill_fights]

        return player_id_job_mapping, cast_events

         