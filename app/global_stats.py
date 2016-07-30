from app import models, db

antag_objective_victory_modes = ["traitor+changeling", "double agents", "autotraitor", "changeling", "vampire"]
objective_success_threshold = 0.8

class MatchTypeVictory:
    victory = False
    secret = False
    mode = None
    def __init__(self, v, s, m):
        if(v): self.victory = v
        if(s): self.secret = s
        if(m): self.mode = m
    def __str__(self):
        return 'Mode: %s Victory: %s Secret: %s' % (self.mode, self.victory, self.secret)

def get_global_stats():
    m = match_stats()

    victories = dict()
    total = dict()

    for match in m:
        if not match.mode in victories:
            victories[match.mode] = {'wins': 0,'losses': 0}
            victories[match.mode]['wins'] = 0
            victories[match.mode]['losses'] = 0
        if match.victory == True:
            victories[match.mode]['wins'] = victories[match.mode]['wins'] + 1
        else:
            victories[match.mode]['losses'] = victories[match.mode]['losses'] + 1
    return victories

def match_stats():
    q = db.session.query(models.Match).all()

    matches = []

    for match in q:
        if 'mixed' in match.mastermode or '|' in match.modes_string:
            continue
        victory = checkModeVictory(match)
        s = True if match.mastermode == "secret" else False
        t = match.modes_string
        m = MatchTypeVictory(victory, s, t)
        matches.append(m)
    return matches


def checkModeVictory(match):
    modestring = match.modes_string.decode('utf-8').lower()
    if modestring == "nuclear emergency" or "malfunction" in modestring:
        if match.nuked == True:
            return True
        else:
            return False
    elif "cultist" in modestring:
        if match.CultStats.narsie_summoned:
            return True
        else:
            return False
    elif "meteor" in modestring:
        return False # No one wins in meteor let's be honest
    elif any(modestring in s for s in antag_objective_victory_modes):
        succeeded = 0
        total = 0
        for objective in match.antagobjs:
            total+=1
            if objective.objective_succeeded:
                succeeded+=1
        if succeeded == 0:
            return False
        elif total == 0:
            return False
        ratio = succeeded/total
        print ratio, succeeded, total
        if ratio >= objective_success_threshold:
            return True
        else:
            return False
