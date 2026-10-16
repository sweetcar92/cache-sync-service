#!/usr/bin/env python3
"""
Parallel epub generation utility using ebook-convert with 2 workers.
"""

import os
import sys
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo


def get_tasks(date_file):
    tasks = [
        ("Le Monde", "r_mod_01.recipe", f"Le_Monde_{date_file}.epub", {}),
        ("Le Parisien", "r_mod_02.recipe", f"Le_Parisien_{date_file}.epub", {}),
        ("Les Echos", "r_mod_03.recipe", f"Les_Echos_{date_file}.epub", {}),
        ("Le Figaro", "r_mod_04.recipe", f"Le_Figaro_{date_file}.epub", {}),
        ("Washington Post", "r_mod_05.recipe", f"Washington_Post_{date_file}.epub", {}),
        ("Courrier International", "r_mod_06.recipe", f"Courrier_International_{date_file}.epub", {}),
        ("The Guardian", "r_mod_07.recipe", f"The_Guardian_{date_file}.epub", {}),
        ("BBC News", "r_mod_08.recipe", f"BBC_News_{date_file}.epub", {}),
    ]

    # Afternoon run check (between 14h and 23h Paris time) for New York Times
    hour = datetime.now(ZoneInfo('Europe/Paris')).hour
    if 14 <= hour <= 23:
        nyt_env = {
            "ZENROWS_KEY": os.environ.get("ZENROWS_KEY", ""),
            "SCRAPEOPS_KEY": os.environ.get("SCRAPEOPS_KEY", ""),
            "SCRAPEOPS_KEY_BACKUP": os.environ.get("SCRAPEOPS_KEY_BACKUP", ""),
        }
        tasks.append(("The New York Times", "r_mod_09.recipe", f"The_New_York_Times_{date_file}.epub", nyt_env))
    else:
        print("⏩ NYT ignoré pour le passage du matin (réservé à l'édition de 17h pour économiser les crédits)")

    return tasks


def run_task(item):
    name, recipe, output_epub, extra_env = item
    start = time.time()
    print(f"🚀 [{name}] Début de la génération...", flush=True)

    env = os.environ.copy()
    env.update(extra_env)

    cmd = ["ebook-convert", recipe, output_epub, "--no-svg-cover"]
    try:
        proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        duration = round(time.time() - start, 1)
        if proc.returncode == 0:
            print(f"✅ [{name}] Terminé avec succès en {duration}s -> {output_epub}", flush=True)
            return True
        else:
            print(f"⚠️ [{name}] Échec après {duration}s (code {proc.returncode})", flush=True)
            if proc.stdout:
                tail = "\n".join(proc.stdout.strip().splitlines()[-25:])
                print(f"--- Extrait log [{name}] ---\n{tail}\n---------------------------", flush=True)
            return False
    except Exception as e:
        print(f"❌ [{name}] Exception: {e}", flush=True)
        return False


def main():
    date_file = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('DATE_FILE')
    if not date_file:
        date_file = datetime.now(ZoneInfo('Europe/Paris')).strftime('%Y-%m-%d_%Hh%M')

    tasks = get_tasks(date_file)
    print(f"=== Lancement de la génération pour {len(tasks)} journaux (2 workers en parallèle) ===", flush=True)
    start_total = time.time()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(run_task, tasks))

    success_count = sum(1 for r in results if r)
    total_duration = round(time.time() - start_total, 1)
    print(f"\n=== Bilan : {success_count}/{len(tasks)} journaux générés avec succès en {total_duration}s ===", flush=True)


if __name__ == '__main__':
    main()
