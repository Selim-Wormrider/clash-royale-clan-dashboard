#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import datetime
from collections import defaultdict

sys.path.append("/opt/dashboard")

from backend.models import Base, RiverRaceHistory
from backend.database import SessionLocal, engine

print("🔧 Upgrading DB with eligibility fields...")

model_path = Path("backend/models.py")
models = model_path.read_text()

if "weeksParticipated" not in models:
    models += """

    weeksParticipated = Column(Integer, default=0)
    weeksMissed = Column(Integer, default=0)
    eligiblePromotion = Column(Boolean, default=False)
    atRiskDemotion = Column(Boolean, default=False)
"""
    model_path.write_text(models)

Base.metadata.create_all(bind=engine)

print("🧠 Calculating 4-week promotion/demotion logic...")

db = SessionLocal()
week_now = datetime.datetime.utcnow().isocalendar()[1]
weeks = [week_now - i for i in range(4)]
entries = db.query(RiverRaceHistory).filter(RiverRaceHistory.week.in_(weeks)).all()

history_map = defaultdict(list)
for e in entries:
    history_map[e.tag].append(e)

for tag, records in history_map.items():
    records.sort(key=lambda r: r.week)
    participated, missed, total = 0, 0, len(weeks)

    for r in records:
        if r.excused:
            total -= 1
        elif r.decks_used >= 4:
            participated += 1
        else:
            missed += 1

    eligible = (participated == total and total >= 2)
    at_risk = (total > 0 and missed / total >= 0.3)

    for r in records:
        r.weeksParticipated = participated
        r.weeksMissed = missed
        r.eligiblePromotion = eligible
        r.atRiskDemotion = at_risk

db.commit()
db.close()
print("✅ Promotion logic complete.")
