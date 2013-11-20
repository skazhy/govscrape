#! /bin/env python

from containers import Calendar

# Create calendar for current (11th) term
cal = Calendar(11)

for session in cal.sessions:
    print session
