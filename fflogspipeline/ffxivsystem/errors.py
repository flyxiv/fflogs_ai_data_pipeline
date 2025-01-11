""" Defines fflogs_rotation_pipeline specific error types
"""

class FfxivRotationPipelineInvalidJobName(Exception):
    """ Raised when an invalid FFXIV combat job name tries to get parsed
    """
    def __init__(self, message):
        super().__init__(message) 
    
class FfxivRotationPipelineInvalidPartySize(Exception):
    """ Raised when there is an invalid number of party members in the fight.
    """ 

    def __init__(self, message):
        super().__init__(message)
         