import unittest
import fflogspipeline.util as util
from fflogspipeline.ffxivsystem.job import FfxivCombatJob, FFXIV_COMBAT_JOB_TO_JOB_NAMES_MAPPING
from fflogspipeline.rotationlog.fflogs_report_parser import FflogsReportParser, CAST_EVENT_TYPE_NAME

class FflogsReportParserTest(unittest.TestCase):
    """Test cases for FflogsReportParser 

    This test case makes assumption that report GkTY1xjrcWq2JAQg is present in fflogs.
    If the logs becomes invalid due to expiration date the test needs to be fixed.
    """

    @classmethod
    def setUpClass(cls):
        cls.report_parser = FflogsReportParser(util.USERNAME, util.KEY)
    
    def test_parse_report(self):
        report_key = 'GkTY1xjrcWq2JAQg'
        
        fight_datas = self.report_parser.parse_report(report_key)
        fight_datas_cnt = len(fight_datas)
        
        assert fight_datas_cnt == 1, f'There is one kill fight in the report, but parser got {fight_datas_cnt} kill fights'
        
        fight_data = fight_datas[0]
        
        assert fight_data.report_key == report_key, f"report_key of fight data must be {report_key}, but got {fight_data.report_key}"
        assert fight_data.fight_id == 3, f"Fight # of kill fight is 3, but parser's fight id is {fight_data.fight_id}"
        
        answers = {
            4: FfxivCombatJob.Bard,
            3: FfxivCombatJob.Dragoon,
            7: FfxivCombatJob.Ninja,
            2: FfxivCombatJob.Pictomancer,
            9: FfxivCombatJob.Astrologian,
            6: FfxivCombatJob.Scholar,
            8: FfxivCombatJob.Darkknight,
            5: FfxivCombatJob.Warrior
        }

        
        for player_id, answer in answers.items():
            parser_player_job = fight_data.player_id_job_mapping[player_id]
            assert answer == parser_player_job, f"player_id {player_id}'s job has to be {FFXIV_COMBAT_JOB_TO_JOB_NAMES_MAPPING[answer]}, but parser gave {FFXIV_COMBAT_JOB_TO_JOB_NAMES_MAPPING[parser_player_job]}"
        
        for event in fight_data.events:
            assert event['type'] == CAST_EVENT_TYPE_NAME, f"all events parsed must be {CAST_EVENT_TYPE_NAME} type, but got {event['type']}"
        
if __name__ == '__main__':
    unittest.main()