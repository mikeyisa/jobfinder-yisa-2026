"""Proximity scoring to Michael's preferred geography. Higher = closer/better.
Order: Austin > Houston/Dallas > rest of TX > Atlanta > NYC > NJ > Oregon >
Arizona > Colorado > US-remote > other US > international."""

# (keywords, score, label) — checked in order, first match wins.
_TIERS = [
    (("austin",), 100, "Austin ★"),
    (("houston",), 93, "Houston"),
    (("dallas", "fort worth", "plano", "irving", "richardson"), 93, "Dallas"),
    (("san antonio",), 86, "San Antonio"),
    (("texas", ", tx", " tx "), 84, "Texas"),
    (("atlanta", "georgia", ", ga"), 78, "Atlanta"),
    (("new york", "nyc", "manhattan", "brooklyn", ", ny"), 72, "New York"),
    (("new jersey", ", nj", "jersey city", "newark", "hoboken"), 70, "New Jersey"),
    (("portland", "oregon", ", or"), 63, "Oregon"),
    (("phoenix", "arizona", ", az", "tempe", "scottsdale"), 58, "Arizona"),
    (("denver", "boulder", "colorado", ", co"), 55, "Colorado"),
]

_INTL = ("canada", "toronto", "ontario", "vancouver", "united kingdom", " uk",
         "london", "ireland", "dublin", "germany", "berlin", "munich", "france",
         "paris", "spain", "portugal", "lisbon", "poland", "netherlands",
         "amsterdam", "australia", "sydney", "singapore", "india", "bangalore",
         "bengaluru", "hyderabad", "brazil", "mexico", "israel", "tel aviv",
         "japan", "tokyo", "china", "emea", "apac", "latam", "europe")


def proximity(loc: str) -> tuple[int, str]:
    if not loc:
        return 50, "Unspecified"
    l = f" {loc.lower()} "
    for kws, score, label in _TIERS:
        if any(k in l for k in kws):
            return score, label
    if "remote" in l:
        if any(c in l for c in _INTL):
            return 15, "Remote (intl)"
        return 80, "Remote (US)"
    if any(c in l for c in _INTL):
        return 8, "International"
    return 30, "US — other"
