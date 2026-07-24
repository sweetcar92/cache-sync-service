import os
import re
from datetime import datetime

DAYS_FR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

def get_day_name():
    return DAYS_FR[datetime.now().weekday()]

def get_series_index():
    return datetime.now().strftime('%Y%m%d%H%M')

print("Day name:", get_day_name())
print("Series index:", get_series_index())
