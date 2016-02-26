from app import models, db

antag_objective_victory_modes = ["traitor+changeling", "double agents", "autotraitor", "changeling"]
objective_success_threshold = 0.8

class MatchTypeVictory:
    victory = False
    secret = False
    mode = None
    def __init__(self, v, s, m):
        if(v): self.victory = v
        if(s): self.secret = s
        if(m): self.mode = m

def get_global_stats():
    m = match_stats()
    print(m)

    victories = dict()

    for match in m:
        print(match.mode)
        if not match.mode in victories:
            victories[match.mode] = {'wins': 0,'losses': 0}
            victories[match.mode]['wins'] = 0
            victories[match.mode]['losses'] = 0
        if match.victory:
            victories[match.mode]['wins'] = victories[match.mode]['wins'] + 1
        else:
            victories[match.mode]['wins'] = victories[match.mode]['losses'] + 1
    return victories

def match_stats():
    q = db.session.query(models.Match).all()

    matches = []

    for match in q:
        victory = checkModeVictory(match)
        if match.mastermode == "mixed":
            continue
        if victory:
            s = True if match.mastermode == "secret" else False
            t = match.modes_string
            m = MatchTypeVictory(victory, s, t)
            matches.append(m)
    return matches


def checkModeVictory(match):
    if match.modes_string.lower() == "nuclear emergency" or match.modes_string.lower() in "malfunction":
        if match.nuked:
            return True
        else:
            return False
    elif any(match.modes_string.lower() in s for s in antag_objective_victory_modes):
        succeeded = 0
        failed = 0
        for objective in match.antagobjs:
            if objective.objective_succeeded:
                succeeded+=1
            else:
                failed+=1
        if succeeded/succeeded+failed >= objective_success_threshold:
            return True
        else:
            return False
