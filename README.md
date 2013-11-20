# govscrape

Latvian parliament (open) data scraper. An early snapshot of work in progress.
Based on scraper toolkit by @jbaiza.


To get all sessions from the current (11th) term:

    from containers import Calendar

    c = Calendar(11)

    for session in c.sessions:
        print session
