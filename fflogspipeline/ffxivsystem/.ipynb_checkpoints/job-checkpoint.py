""" Implements classes and enums needed to define Ffxiv combat jobs
"""

from enum import Enum

class FfxivCombatJob(Enum):
    Paladin = 1
    Warrior = 2
    Darkknight = 3
    Gunbreaker = 4
    
    Whitemage = 5
    Scholar = 6
    Astrologian = 7
    Sage = 8
    
    Dragoon = 9
    Monk = 10
    Ninja = 11
    Samurai = 12
    Reaper = 13
    Viper = 14
    
    Bard = 15
    Machinist = 16
    Dancer = 17
    
    Blackmage = 18
    Summoner = 19
    Redmage = 20
    Pictomancer = 21 

FFXIV_COMBAT_JOB_TO_JOB_NAMES_MAPPING = {
    FfxivCombatJob.Paladin: "Paladin",
    FfxivCombatJob.Warrior: "Warrior",
    FfxivCombatJob.Darkknight: "Dark Knight",
    FfxivCombatJob.Gunbreaker: "Gunbreaker",
    
    FfxivCombatJob.Whitemage: "White Mage",
    FfxivCombatJob.Scholar: "Scholar",
    FfxivCombatJob.Astrologian: "Astrologian",
    FfxivCombatJob.Sage: "Sage",
    
    FfxivCombatJob.Dragoon: "Dragoon",
    FfxivCombatJob.Monk: "Monk",
    FfxivCombatJob.Ninja: "Ninja",
    FfxivCombatJob.Samurai: "Samurai",
    FfxivCombatJob.Reaper: "Reaper",
    FfxivCombatJob.Viper: "Viper",
    
    FfxivCombatJob.Bard: "Bard",
    FfxivCombatJob.Machinist: "Machinist",
    FfxivCombatJob.Dancer: "Dancer",
    
    FfxivCombatJob.Blackmage: "Black Mage",
    FfxivCombatJob.Summoner: "Summoner",
    FfxivCombatJob.Redmage: "Red Mage",
    FfxivCombatJob.Pictomancer: "Pictomancer"
}

FFXIV_JOB_NAMES_TO_COMBAT_JOB_MAPPING = {
    "Paladin":     FfxivCombatJob.Paladin,
    "Warrior":     FfxivCombatJob.Warrior,
    "Dark Knight":     FfxivCombatJob.Darkknight,
    "Gunbreaker":     FfxivCombatJob.Gunbreaker,
    
    "White Mage":     FfxivCombatJob.Whitemage,
    "Scholar":     FfxivCombatJob.Scholar,
    "Astrologian":     FfxivCombatJob.Astrologian,
    "Sage":     FfxivCombatJob.Sage,
    
    "Dragoon":     FfxivCombatJob.Dragoon,
    "Monk":     FfxivCombatJob.Monk,
    "Ninja":     FfxivCombatJob.Ninja,
    "Samurai":     FfxivCombatJob.Samurai,
    "Reaper":     FfxivCombatJob.Reaper,
    "Viper":     FfxivCombatJob.Viper,
    
    "Bard":     FfxivCombatJob.Bard,
    "Machinist":     FfxivCombatJob.Machinist,
    "Dancer":     FfxivCombatJob.Dancer,
    
    "Black Mage":     FfxivCombatJob.Blackmage,
    "Summoner":     FfxivCombatJob.Summoner,
    "Red Mage":     FfxivCombatJob.Redmage,
    "Pictomancer": FfxivCombatJob.Pictomancer
}