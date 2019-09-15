# GDPR

Two Years Later, and A Few Euros Shorter: Real-world Impact of GDPR
------------------------------------------------------------
The General Data Protection Regulation (GDPR) is a set of regulations
introduced by Europe that seeks to protect user privacy. It provides
users with new rights.  Several companies, including Google, have been
fined for violating GDPR. We would like to study these rulings.

The goal is to design and maintain an auto-updating repository of all
the GDPR rulings and penalties. Currently, no official or
comprehensive datasets exist for this. The best we have found are the
UK ICO's enforcement tracker
(https://ico.org.uk/action-weve-taken/enforcement/), and an adhoc
marketing effort by a law firm (http://www.enforcementtracker.com/).

In addition to serving as a reference on all things GDPR, this
repository also allows us to do high-level analysis. For e.g.,
questions like "how many times has article-14 been violated", or "how
many IoT related fines have been imposed" etc can be answered with
simple queries. It would seed systems researchers with accurate
information to build mechanisms and tools that help avoid GDPR fines.

This task is not as trivial as it seems: (i) this data comes from 28
independent regulators spread throughout EU countries, each of them
publishing rulings at a time of their choosing in their own formats
(most of them not even in English); (ii) given the frequency of
updates, populating a repository should necessarily be automated;
(iii) finally, each of the valid auto-populated entries need to be
technically analyzed (a manual effort that should be minimized or
avoided using NLP techniques).
