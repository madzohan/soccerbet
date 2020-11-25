def parse_top_matches(data: dict) -> dict:
    for match in data.get('Value', []):
        try:
            yield dict(id=match['I'], o1=match['O1'], o2=match['O2'])
        except (IndexError, KeyError):
            continue


def parse_match_coefs(data: dict) -> dict:
    coefs = {}
    try:
        events = data['Value']['GE'][0]['E']
        score = data['Value']['SC']['FS']
        coefs = dict(id=data['Value']['I'], o1=events[0][0]['C'], x=events[1][0]['C'], o2=events[2][0]['C'],
                     s1=score.get('S1', 0), s2=score.get('S2', 0))
    except (IndexError, KeyError):
        pass
    return coefs
