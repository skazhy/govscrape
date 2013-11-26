#! /bin/env python

from containers import Calendar, Deputies

# Create calendar for current (11th) term
cal = Calendar(11)

for session in cal.sessions:
    print session

# Lookup all votings in the first session of 11th term
for voting in cal.sessions[0].votings:
    print voting
sessions[0].drop()  # cleanup

# Get a list of all deputies in current (11th) term
deputies = Deputies(11)

for deputy in deputies.deputies:
    print deputy
