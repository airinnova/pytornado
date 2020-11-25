import json

settings_file = 'pytornado/settings/template.json'

with open(settings_file, 'r') as fp:
    settings = json.load(fp)

settings['plot']['results']['show'] = False
settings['plot']['results']['save'] = True

with open(settings_file, 'w') as fp:
    json.dump(settings, fp, indent=4, separators=(',', ': '))
