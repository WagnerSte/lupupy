"""What the panel's web interface says each kind of device can do.

This is not part of the manufacturer's specification. It is the device table
of the panel's own web interface, copied from /js/script.js of an XT1 Plus on
2026-09-18, and a firmware update is free to change it. The names of the
skills are the interface's own.

Devices are grouped by the prefix of their id. Zigbee devices ("ZS") are
listed by the Zigbee profile and device number, which only deviceGet
reports; every other group is listed by the device type that the device
list carries as well. Some groups name the calls that serve a skill, such as
the call that sends a Zigbee device a level.

The interface adds a few skills at runtime from other fields of a device,
for example bypass for alarm zones. Those rules are not reproduced here, so
this is what a kind of device can do rather than everything a particular
one is set up for.

Observed on an XT1 Plus; not verified against other models or firmware
versions.
"""

from dataclasses import dataclass, field

ZIGBEE = "ZS"
UNKNOWN_GROUP = "00"

DEVICE_TABLE: dict = {   '00': {'0': {'skills': [], 'desc': 'Unknown Device'}},
    'ZS': {   '0': {'0': {'skills': [], 'desc': 'Unknown device'}},
              '260': {   'actions': {   'pss': 'deviceSwitchPSSPost',
                                        'groupPss': 'groupSwitchPost',
                                        'group': 'deviceGroupPost',
                                        'color': 'deviceHueColorControl',
                                        'level': 'deviceSwitchDimmerPost'},
                         '0': {'skills': ['onOff', 'toggle'], 'desc': 'On/Off Switch'},
                         '1': {   'skills': ['level', 'dimmer'],
                                  'desc': 'Level Control Switch'},
                         '2': {'skills': ['onOff'], 'desc': 'On/Off Output'},
                         '3': {   'skills': ['level', 'dimmer'],
                                  'desc': 'Level Controllable Output'},
                         '4': {'skills': ['trigger_scene'], 'desc': 'Scene Selector'},
                         '5': {'skills': [], 'desc': 'Configuration Tool'},
                         '6': {'skills': ['armDisarm'], 'desc': 'Remote Control'},
                         '7': {'skills': [], 'desc': 'Combined Interface'},
                         '8': {'skills': [], 'desc': 'Range Extender'},
                         '9': {   'skills': ['group', 'pss', 'onOff', 'toggle'],
                                  'desc': 'Mains Power Outlet'},
                         '10': {'skills': ['openClose', 'latch'], 'desc': 'Door Lock'},
                         '11': {'skills': [], 'desc': 'Door Lock Controller'},
                         '12': {'skills': [], 'desc': 'Simple Sensor'},
                         '13': {'skills': [], 'desc': 'Consumption Awareness Device'},
                         '80': {'skills': [], 'desc': 'Home Gateway'},
                         '81': {   'skills': [   'schedule',
                                                 'onOff',
                                                 'toggle',
                                                 'period',
                                                 'power'],
                                   'desc': 'Smart Plug'},
                         '82': {'skills': [], 'desc': 'White Goods'},
                         '83': {'skills': [], 'desc': 'Meter Interface'},
                         '256': {   'skills': ['schedule', 'group', 'onOff', 'toggle'],
                                    'desc': 'On/Off Light'},
                         '257': {   'skills': [   'schedule',
                                                  'group',
                                                  'onOff',
                                                  'toggle',
                                                  'period',
                                                  'dimmer'],
                                    'desc': 'Dimmable Light'},
                         '258': {   'skills': [   'schedule',
                                                  'group',
                                                  'onOff',
                                                  'toggle',
                                                  'dimmer'],
                                    'desc': 'Color Dimmable Light'},
                         '259': {   'skills': ['onOff', 'toggle'],
                                    'desc': 'On/Off Light Switch'},
                         '260': {   'skills': ['schedule', 'onOff', 'toggle', 'dimmer'],
                                    'desc': 'Dimmer Switch'},
                         '261': {   'skills': ['onOff', 'toggle', 'dimmer'],
                                    'desc': 'Color Dimmer Switch'},
                         '262': {'skills': ['lux'], 'desc': 'Light Sensor'},
                         '263': {'skills': [], 'desc': 'Occupancy Sensor'},
                         '268': {   'skills': ['onOff', 'toggle', 'period', 'dimmer'],
                                    'desc': 'Extended color light'},
                         '269': {   'skills': ['onOff', 'toggle', 'period', 'dimmer'],
                                    'desc': 'Extended color light'},
                         '512': {'skills': ['upDown'], 'desc': 'Shade'},
                         '514': {   'skills': ['upDown', 'stop', 'level'],
                                    'desc': 'Window Covering Device'},
                         '515': {'skills': [], 'desc': 'Window Covering Controller'},
                         '768': {'skills': [], 'desc': 'Heating/Cooling Unit'},
                         '769': {   'skills': ['onOff', 'temp', 'setTemp'],
                                    'desc': 'Thermostat'},
                         '770': {'skills': ['temp'], 'desc': 'Temperature Sensor'},
                         '771': {'skills': ['onOff', 'toggle'], 'desc': 'Pump'},
                         '772': {'skills': [], 'desc': 'Pump Controller'},
                         '773': {'skills': [], 'desc': 'Pressure Sensor'},
                         '774': {'skills': ['flow'], 'desc': 'Flow Sensor'},
                         '775': {'skills': [], 'desc': 'Mini Split AC'},
                         '1019': {   'skills': ['alertVisual'],
                                     'desc': 'IAS Warning Device'},
                         '1024': {   'skills': [],
                                     'desc': 'IAS Control and Indicating Equipment'},
                         '1025': {   'skills': [],
                                     'desc': 'IAS Ancillary Control Equipment'},
                         '1026': {'skills': ['triggerAlert'], 'desc': 'IAS Zone'},
                         '1027': {   'skills': ['alertAudio'],
                                     'desc': 'IAS Warning Device'},
                         '1028': {'skills': ['detectMotion'], 'desc': 'PIR Sensor'},
                         '2048': {   'skills': ['onOff', 'toggle'],
                                     'desc': 'Remote switch'}},
              '49246': {   'actions': {   'pss': 'deviceSwitchPSSPost',
                                          'groupPss': 'groupSwitchPost',
                                          'group': 'deviceGroupPost',
                                          'color': 'deviceHueColorControl',
                                          'level': 'deviceSwitchDimmerPost'},
                           '0': {   'skills': [   'schedule',
                                                  'group',
                                                  'pss',
                                                  'onOff',
                                                  'toggle'],
                                    'desc': 'On/Off light'},
                           '16': {   'skills': [   'schedule',
                                                   'group',
                                                   'pss',
                                                   'onOff',
                                                   'toggle'],
                                     'desc': 'On/Off plug-in unit'},
                           '256': {   'skills': [   'schedule',
                                                    'group',
                                                    'pss',
                                                    'onOff',
                                                    'toggle',
                                                    'period',
                                                    'dimmer'],
                                      'desc': 'Dimmable light'},
                           '272': {   'skills': [   'schedule',
                                                    'group',
                                                    'pss',
                                                    'onOff',
                                                    'toggle',
                                                    'dimmer'],
                                      'desc': 'Dimmable plug-in unit'},
                           '512': {   'skills': [   'schedule',
                                                    'group',
                                                    'pss',
                                                    'onOff',
                                                    'toggle',
                                                    'period',
                                                    'dimmer'],
                                      'desc': 'Color light'},
                           '528': {   'skills': [   'schedule',
                                                    'group',
                                                    'pss',
                                                    'onOff',
                                                    'toggle',
                                                    'period',
                                                    'dimmer'],
                                      'desc': 'Extended color light'},
                           '544': {   'skills': [   'schedule',
                                                    'group',
                                                    'pss',
                                                    'onOff',
                                                    'toggle',
                                                    'period',
                                                    'dimmer'],
                                      'desc': 'Color temperature light'},
                           '2128': {   'skills': ['triggerAlert', 'detectMotion'],
                                       'desc': 'Outdoor Sensor'}}},
    'EX': {   '0': {   '4': {   'skills': ['triggerAlert', 'detectOpenClose'],
                                'desc': 'Contact switch'},
                       '24': {'skills': ['onOff'], 'desc': '12V/24V Relais'}}},
    'RF': {   'actions': {   'pss': 'deviceSwitchPSSPost',
                             'groupPss': 'groupSwitchPost',
                             'group': 'deviceGroupPost',
                             'color': 'deviceHueColorControl',
                             'level': 'deviceSwitchDimmerPost'},
              '2': {'skills': ['armDisarm', 'triggerAlert'], 'desc': 'Remote Control'},
              '4': {   'skills': ['triggerAlert', 'triggerOpenClose'],
                       'desc': 'Contact switch'},
              '5': {'skills': ['triggerAlert', 'detectWater'], 'desc': 'Water sensor'},
              '7': {'skills': ['triggerAlert', 'triggerPanic'], 'desc': 'Panic button'},
              '9': {   'skills': ['triggerAlert', 'detectMotion'],
                       'desc': 'PIR Motion detection'},
              '10': {   'skills': ['triggerAlert', 'detect_motion'],
                        'desc': 'Outdoor PIR Motion detection'},
              '11': {   'skills': ['triggerAlert', 'detectFireSmoke'],
                        'desc': 'Firesensor'},
              '12': {   'skills': ['triggerAlert', 'detectFireSmoke'],
                        'desc': 'Gassensor'},
              '13': {'skills': ['triggerAlert', 'co2'], 'desc': 'CO sensor'},
              '16': {'skills': ['triggerAlert'], 'desc': 'Tag Reader'},
              '17': {'skills': ['armDisarm', 'triggerAlert'], 'desc': 'Remote Control'},
              '21': {   'skills': ['triggerAlert', 'triggerMedic'],
                        'desc': 'Medical emergency'},
              '22': {   'skills': ['triggerAlert', 'alertVisual', 'alertVisual'],
                        'desc': 'Warning device(Indoor)'},
              '33': {'skills': [], 'desc': 'Generic Sensor Control'},
              '36': {'skills': [], 'desc': 'Generic Sensor Control'},
              '37': {'skills': ['armDisarm', 'triggerAlert'], 'desc': 'Remote Control'},
              '39': {   'skills': ['triggerAlert', 'detectGlass', 'detectVibration'],
                        'desc': 'Glassbreak/Vibration sensor'},
              '45': {   'skills': ['triggerAlert', 'alertVisual', 'alertAudio'],
                        'desc': 'Warning device(Indoor)'},
              '46': {   'skills': ['triggerAlert', 'alertVisual', 'alertAudio'],
                        'desc': 'Warning device(Outdoor)'},
              '48': {'skills': ['onOff', 'toggle'], 'desc': 'Power Switch'},
              '58': {'skills': ['detectFireSmoke'], 'desc': 'Warning device(Heat)'},
              '93': {   'skills': ['triggerAlert', 'detectGlass', 'detectVibration'],
                        'desc': 'Glassbreak/Vibration sensor'}},
    'IP': {   '0': {'skills': [], 'desc': 'Generic IPCam'},
              '10': {'skills': [], 'desc': 'LUPUSNET HD'},
              '11': {'skills': [], 'desc': 'LUPUSNET HD PZT'},
              '201': {'skills': [], 'desc': 'Lupus LE201 IPCam'},
              '202': {'skills': [], 'desc': 'Lupus LE202 IPCam'},
              '203': {'skills': [], 'desc': 'Lupus LE203 IPCam'},
              '204': {'skills': [], 'desc': 'Lupus LE204 IPCam'}},
    'NK': {   'actions': {'pss': 'nukiCmd'},
              '57': {   'skills': ['schedule', 'pss', 'openClose', 'latch'],
                        'desc': 'Door Lock V1'},
              '1': {   'skills': [   'schedule',
                                     'triggerAlert',
                                     'openClose',
                                     'latch',
                                     'detectOpenClose'],
                       'desc': 'Door Lock V2'}},
    'NE': {   '54': {   'skills': ['temp', 'humidity', 'co2', 'noise', 'gust'],
                        'desc': 'Weather station'},
              '541': {'skills': ['temp', 'moisture'], 'desc': 'Outdoor modul'},
              '542': {'skills': ['windSpeed', 'windDir'], 'desc': 'Wind sensor'},
              '543': {'skills': ['rainfall'], 'desc': 'Rain sensor'}},
    'GH': {   '24': {'skills': ['pss', 'onOff', 'toggle'], 'desc': 'Power Switch'},
              '78': {'skills': ['lux', 'humidity', 'temp'], 'desc': 'Plant Sensor'},
              '96': {'skills': ['pss', 'temp', 'onOff'], 'desc': 'Water control'},
              '108': {'skills': ['pss', 'startStop', 'playPause'], 'desc': 'Mower'}},
    'SO': {   'action': {'pss': 'sonosPost'},
              '107': {   'skills': [   'pss',
                                       'volume',
                                       'nextPrev',
                                       'playPause',
                                       'playlist',
                                       'stop',
                                       'alertAudio',
                                       'pressure',
                                       'title',
                                       'setTitle'],
                         'desc': 'Generic SONOS'}},
    'LD': {   '67': {   'skills': ['site', 'location', 'lonlat', 'room'],
                        'desc': 'Generic LD'}}}


@dataclass(frozen=True)
class Capability:
    """What the web interface says one kind of device can do."""

    description: str
    skills: frozenset[str]
    actions: dict[str, str] = field(default_factory=dict)

    def can(self, skill: str) -> bool:
        """Whether the interface offers this skill for the device."""
        return skill in self.skills


def lookup(
    device_id: str,
    device_type: int | None = None,
    profile: int | None = None,
    device: int | None = None,
) -> Capability | None:
    """Find what a device can do, or None if the table does not know it.

    device_type is the type from the device list. Zigbee devices need the
    profile and device numbers from deviceGet instead.
    """
    group = device_id.split(":", 1)[0] if ":" in device_id else UNKNOWN_GROUP
    entries = DEVICE_TABLE.get(group)
    if entries is None:
        return None

    if group == ZIGBEE:
        entries = entries.get(str(profile))
        key = device
    else:
        key = device_type
    if entries is None or key is None:
        return None

    entry = entries.get(str(key))
    if not isinstance(entry, dict) or "skills" not in entry:
        return None

    # One group spells it "action".
    actions = entries.get("actions") or entries.get("action") or {}
    return Capability(
        description=entry["desc"],
        skills=frozenset(entry["skills"]),
        actions=dict(actions) if isinstance(actions, dict) else {},
    )
