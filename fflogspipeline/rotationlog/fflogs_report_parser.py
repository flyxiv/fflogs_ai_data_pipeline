""" Parses needed information from report collected by FFLogsApi

FFLogs AI data pipeline only needs combat related events, which are cast events
"""

from fflogspipeline.ffxivsystem.job import FFXIV_JOB_NAMES_TO_COMBAT_JOB_MAPPING
from fflogspipeline.ffxivsystem.errors import FfxivRotationPipelineInvalidPartySize, FfxivRotationPipelineInvalidJobName
from fflogsapi import FFLogsClient
from dataclasses import dataclass
from typing import List

CAST_EVENT_TYPE_NAME = 'cast'
FFXIV_STANDARD_PARTY_SIZE = 8

@dataclass
class FightData:
    """Struct containing combat related information of a fight
    """
    report_key: str
    fight_id: int
    player_id_job_mapping: dict
    events: list[dict]


class FflogsReportParser:
    def __init__(self, username, key):
        self.client = FFLogsClient(username, key)
    
    def __fetch_report(self, report_key: str):
        return self.client.get_report(report_key)

    def __create_player_id_to_job_mapping(self, player_details):
        """ Creates player id -> FfxivCombatJob enum mapping for the players in the fight

        Raises:
           1) FfxivRotationPipelineInvalidJobName if the job name is not in the ffxiv job to job name mapping
           2) FfxivRotationPipelineInvalidPartySize if the party size is invalid
        """
        player_id_to_job_mapping = {}
        for player_detail in player_details:
            job_name = player_detail.job.name
            
            if job_name in FFXIV_JOB_NAMES_TO_COMBAT_JOB_MAPPING:
                player_id_to_job_mapping[player_detail.id] = FFXIV_JOB_NAMES_TO_COMBAT_JOB_MAPPING[job_name]
            else:
                raise FfxivRotationPipelineInvalidJobName
               
        if len(player_id_to_job_mapping) != FFXIV_STANDARD_PARTY_SIZE:
            raise FfxivRotationPipelineInvalidPartySize 
            
        return player_id_to_job_mapping 

    def __collect_only_cast_events(self, fight_events):
        return (report_event for report_event in fight_events if report_event['type'] == CAST_EVENT_TYPE_NAME)
    
    def parse_report(self, report_key: str) -> List[FightData]:
        """
        Args: report_key: key url of the report
            ex) If report url is https://www.fflogs.com/reports/41ry2hjTYvFLwJxA, report_key is '41ry2hjTYvFLwJxA'
   
        Returns:
            Parsed result data containing:
                * Dictionary mapping player id to the player's job
                * 'cast' events of the fight
        """
        report = self.__fetch_report(report_key)
        kill_fights = [fight for fight in report.fights() if fight.is_kill() and fight.standard_comp()] 
        fight_ids = [fight.id for fight in kill_fights]
        player_id_job_mappings = [self.__create_player_id_to_job_mapping(kill_fight.player_details()) for kill_fight in kill_fights]

        cast_events_list = [self.__collect_only_cast_events(kill_fight.events()) for kill_fight in kill_fights]

        fight_datas = []

        for (fight_id, player_id_job_mapping, cast_events) in zip(fight_ids, player_id_job_mappings, cast_events_list):
            fight_datas.append(FightData(report_key=report_key, fight_id=fight_id, player_id_job_mapping=player_id_job_mapping, events=cast_events))
        
        return fight_datas
