from ixbet.parser import parse_top_matches, parse_match_coefs


def test_parse_top_matches(top_matches):
    matches_gen = parse_top_matches(top_matches)
    for match in [dict(id=268476092, o1='Labasa', o2='Nasinu'),
                  dict(id=268482441, o1='Colombia+', o2='Spain+'),
                  dict(id=268483251, o1='South Korea (3х3)', o2='Thailand (3х3)'),
                  dict(id=268479518, o1='Manchester United (4х4)', o2='Juventus (4х4)'),
                  dict(id=268479796, o1='Chelsea (4х4)', o2='Liverpool (4х4)')]:
        assert match == next(matches_gen)


def test_parse_match_coefs(coefs):
    assert parse_match_coefs(coefs) == dict(id=268476092, o1=1.14, x=8.59, o2=15.9, s1=1, s2=0)
