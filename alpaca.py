import requests


DEFAULT_API_VERSION = 1


class Equipment:
    def __init__(self, address, device_type, device_number, protocall, api_version):
        self.address = address
        self.device_type = device_type
        self.device_number = device_number
        self.api_version = api_version
        self.base_url = '%s://%s/api/v%d/%s/%d' % (protocall, address, api_version, device_type, device_number)
    
    def action(self, action, *args):
        return requests.put('%s/action' % self.base_url, data={'Action': action, 'Parameters': args})
    
    def commandblind(self, command, raw):
        return requests.put('%s/commandblind' % self.base_url, data={'Command': command, 'Raw': raw})
    
    def commandbool(self, command, raw):
        return bool(requests.put('%s/commandbool' % self.base_url, data={'Command': command, 'Raw': raw}))
    
    def commandstring(self, command, raw):
        return requests.put('%s/commandstring' % self.base_url, data={'Command': command, 'Raw': raw})
    
    def connected(self, connected = None):
        if connected == None:
            return bool(requests.get('%s/connected' % self.base_url).json()['Value'])
        else:
            return requests.put('%s/connected' % self.base_url, data={'Connected': connected})
    
    def description(self):
        return requests.get('%s/description' % self.base_url).json()['Value']
    
    def driverinfo(self):
        return [i.strip() for i in requests.get('%s/driverinfo' % self.base_url).json()['Value'].split(',')]

    def driverversion(self):
        return requests.get('%s/driverversion' % self.base_url).json()['Value']

    def interfaceversion(self):
        return int(requests.get('%s/interfaceversion' % self.base_url).json()['Value'])

    def name(self):
        return requests.get('%s/name' % self.base_url).json()['Value']
    
    def supportedactions(self):
        return requests.get('%s/supportedactions' % self.base_url).json()['Value']
