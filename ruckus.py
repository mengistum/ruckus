"""
This is the first API I worked on to interact with Ruckus SCG200.

Author:     Meheretab Mengistu
Date:       09/29/2020
Version:    2.0
Reference:  Philip Siu Ruckus.py
"""

# Import requests module to work on Ruckus REST API
import requests
import urllib3

# To disable HTTPs related warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Ruckus:
    """
    Ruckus class to instantiate a Ruckus object
    """

    # Initialize the object -- take username, password during initialization
    def __init__(self, controller_ip, port, username, password):

        # URI for SCG 200 to connect to and user_info
        self.scg200_uri = f'https://{controller_ip}:{port}/wsg/api/public'
        user_info = {'username': username, 'password': password}

        # Create session and initiate connection
        self.session = requests.Session()
        self.session.post(f'{self.scg200_uri}/v5_0/session', verify=False, \
                          json=user_info)

        # Get session info, domain_id and zone_id
        self.session_info = self.session.get(f'{self.scg200_uri}/v5_0/session').json()
        self.domain_id = self.session_info['domainId']



    #-------------------------------------------------------------------------
    #   The METHODS below are for general Controller related information!
    #-------------------------------------------------------------------------

    def system_summary(self):
        """
        Retrieve the system summary
        """
        return self.session.get(f'{self.scg200_uri}/v5_0/controller').json()


    def get_ap_count(self):
        """
        Get the total number of APs in the Controller
        """
        ap_count = self.session.get(f'{self.scg200_uri}/v5_0/aps/totalCount',\
                                    params={'domain_id':self.domain_id}\
                                    ).json()
        return ap_count


    def ap_models(self):
        """
        Retrieve all AP Models in the system
        """
        apmodels = self.session.get(f'{self.scg200_uri}/v5_0/system/apmodels')

        if apmodels.status_code==200:
            print('All AP Models on the controller are reported correctly!')
            print('\n\n' + apmodels.text + '\n\n')
        else:
            print('Something went wrong!')




    #----------------------------------------------------------------------
    #  The METHODS below are for ZONE based activities!
    #----------------------------------------------------------------------

    def get_zones(self, zone_id=None):
        """
        Get zone information from the controller

        Parameters:
        zone_id - zone ID number

        Returns:
        zones - json file
        """

        if zone_id is None:
            # Retrieve the list of AP zones that belong to a domain
            zones = self.session.get(f'{self.scg200_uri}/v5_0/rkszones',\
                                      params={'listSize':200}).json()
        else:
            # Retrieve the AP zone configuration
            zones = self.session.get(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}').json()

        return zones



    def get_zone_id(self, zone):
        """
        Get zone_id for a specific zone

        Parameters:
        zone - zone name

        Returns:
        zone_id - string
        """

        # Get all zones info from the controller
        zones = self.get_zones()

        try:
            for site in zones['list']:
                if site['name']==zone:
                    zone_id = site['id']

        except ValueError:
            print('Incorrect zone information!')

        # Return zone_id
        return zone_id




    def create_zone(self, zone_name, ap_login, domain_id=None, description='Test'):
        """
        Create a new zone on the controller

        Parameters:
        zone_name - name for the zone to be created
        ap_login - login credential for the APs
        domain_id - domain Id for the controller
        description - description for the zone

        Returns:
        """

        # Controller Version
        version='3.5.1.0.1026'

        # If no new domain_id info is passed, use the system domain_id
        if domain_id is None:
            domain_id = self.domain_id

        self.session.post(f'{self.scg200_uri}/v5_0/rkszones', json= \
                          {'domain_id': domain_id, 'name': zone_name, \
                           'login': ap_login, 'description': description, \
                           'version': version, 'countryCode': 'US'}).json()

        print(f'Zone {zone_name} --> created successfully!')



    def delete_zone(self, zone):
        """
        Delete a zone

        Parameters:
        zone - zone to delete from the controller

        Returns:
        """

        # Get zone_id from the zone name
        zone_id = self.get_zone_id(zone)

        del_zone = self.session.delete(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}')

        # Print to the user whether the deletion was successful
        if del_zone.status_code==200:
            print(f'Response: {del_zone.status_code}. SUCCESSFULLY DELETED!')
        else:
            print(f'Response: {del_zone.status_code}. FAILED TO DELETE!')



    def modify_zone(self, zone):
        """
        Modify basic information of a zone - specifically DFS Channels

        Parameters:
        zone - zone name

        Returns:
        """

        # Get zone Id
        zone_id = self.get_zone_id(zone)

        mod_zone = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}', \
                                          json={'dfsChannelEnabled': True})

        # Print to the user whether the modification is successful
        if mod_zone.status_code==204:
            print(f'Response: {mod_zone.status_code}. SUCCESS!')
        else:
            print(f'Response: {mod_zone.status_code}. CHANGE FAILED!')



    def channelfly(self, zone, channel='both'):
        """
        Turn ON/OFF channelfly for a zone

        Parameters:
        Zone - zone name
        Channel - channel to work on (2.4, 5.0, both)

        Returns:
        Output:    Response status_code (204)
        """

        # Get zone_id from zone name
        zone_id = self.get_zone_id(zone)

        # Ask whether do you want to turn off channelfly
        turn_off = input('Do you want to DISABLE channelfly (Y/N):  ')

        if turn_off.upper()=='N':
            channelfly = {'channelSelectMode': 'channelfly', 'channelflyMtbc': 300}
        else:
            channelfly = {'channelSelectMode': 'None'}

            if channel=='both':
                print('Turning off channelfly on both 2.4GHz and 5GHz')
                ch24 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/\
                    autoChannelSelection24', json=channelfly)
                ch50 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/\
                    autoChannelSelection50', json=channelfly)
                print('Channel 2.4G Response: ' + str(ch24.status_code))
                print('Channel 5.0G Response: ' + str(ch50.status_code))
                print('\nThe expected response for both Channels is 204!\n')

            elif channel=='2.4':
                print('Turning off channelfly on 2.4GHz')
                ch24 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/\
                    autoChannelSelection24', json=channelfly)
                print('Channel 2.4G Response: ' + str(ch24.status_code))
                print('\nThe expected response is 204!\n')

            elif channel=='5.0':
                print('Turning off channelfly on 5GHz')
                ch50 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/\
                    autoChannelSelection50', json=channelfly)
                print('Channel 5.0G Response: ' + str(ch50.status_code))
                print('\nThe expected response is 204!\n')

            else:
                print('You have entered wrong channel information!')



    def update_ap_login(self, zone, aplogin):
        """
        Change AP Login username/password for a zone

        Parameters:
        zone - zone name
        aplogin - login credentials for the APs

        Returns:
        """

        # Get zone Id from the zone name
        zone_id = self.get_zone_id(zone)

        print('Applying username/password change for AP Login!\n')

        self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/\
            {zone_id}/login', json=aplogin)

        print('Username/password for AP Login is updated!')


    def update_radio(self, zone, channel='both'):
        """
        To modify 2.4G & 5G radio configuration for APs that belong to a zone

        Parameters:
        zone - zone name
        channel - channel to update radio signals

        Returns:
        """

        # Get zone Id
        zone_id = self.get_zone_id(zone)

        # Channels range to work on
        channel_range24 = [1, 6, 11]
        channel_range50 = [36, 44, 52, 60, 100, 108, 132, 149, 157]
        channel_range50_outdoor = [36, 44, 149, 157]

        print('\nThe Acceptable TX Power values for both 2.4GHz and 5GHz are:-')
        print('Full, -1dB, -2dB, -3dB(1/2), -4dB, -5dB, -6dB(1/4), -7dB, -8dB, -9dB(1/8),\
         -10dB, Min\n\n')


        if channel=='both':
            # Ask the user to enter the TX power in dB - the list is provided in the previous print
            tx_power24 = input('Enter TX Power for 2.4GHz:  ')
            tx_power50 = input('Enter TX Power for 5.0GHz:  ')

            wifi24 = {'txPower':tx_power24, 'channelRange':channel_range24}
            wifi50 = {'txPower':tx_power50, 'indoorChannelRange':channel_range50, \
                              'outdoorChannelRange':channel_range50_outdoor}

            # Enable DFS Channels to get 9 usable channels
            self.modify_zone(zone_id)

            ch24 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/wifi24', \
                json=wifi24)
            ch50 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/wifi50', \
                json=wifi50)
            print('Channel 2.4G Response: ' + str(ch24.status_code))
            print('Channel 5.0G Response: ' + str(ch50.status_code))

        elif channel=='2.4':
            tx_power24 = input('Enter TX power for 2.4GHz:  ')
            wifi24 = {'txPower':tx_power24, 'channelRange':channel_range24}
            ch24 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/wifi24', \
                json=wifi24)
            print('Channel 2.4G Response: ' + str(ch24.status_code))

        elif channel=='5.0':
            tx_power50 = input('Enter TX Power for 5.0GHz:  ')
            wifi50 = {'txPower':tx_power50, 'indoorChannelRange':channel_range50, \
                              'outdoorChannelRange':channel_range50_outdoor}

            # Enable DFS Channels to get 9 usable channels
            self.modify_zone(zone_id)

            ch50 = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/wifi50', \
                json=wifi50)
            print('Channel 5.0G Response: ' + str(ch50.status_code))
        else:
            print('You did not enter correct value!')



    #-----------------------------------------------------------
    # The METHODS below are for WLAN based activities!
    #-----------------------------------------------------------

    def get_wlan_id(self, zone_id):
        """
        Get wlan ID for SSIDs

        Parameters:
        zone_id - zone Id value

        Returns:
        wlan_id - string
        """

        # Get wlan List for the selected zone
        wlan_list = self. session.get(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/wlans').json()

        # Get the list of SSIDs and their related info
        wlan_info = wlan_list['list']

        # Initialize wlan_id with 0
        wlan_id = '0'
        # Go over each list until you find "SFUSD" SSID and grab "wlan_id"
        for i in range(0,wlan_list['totalCount']):
            # Return wlan_id if the SSID is 'SFUSD'
            if wlan_info[i]['ssid'] == 'SFUSD':
                wlan_id = wlan_info[i]['id']
                break

        # Return wlan_id
        return wlan_id



    def modify_wlan_auth(self, zone_id, wlan_id, \
        auth_service_name ='F5-VIP-ISE-Radius'):
        """
        Use to change the authentication service profile

        Parameters:
        zone_id - zone ID value
        wlan_id - WLAN ID value
        auth_service_name - Name and UUID for the authentication service profile
                        --> '0df5e802-ab59-11ea-a492-94f6652af50d' for "F5-VIP-ISE-Radius"
                        --> 'd6b860c0-37a4-11e5-a220-94f6652af50d' for "NPS-Radius-Proxy"

        Returns:
        """

        mod_wlan = self.session.patch(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/wlans\
            /{wlan_id}/authServiceOrProfile', json = {'name': auth_service_name})

        # Print to the user whether the change was successful
        if mod_wlan.status_code == 204:
            print(f'Response: {mod_wlan.status_code}. SUCCESS!')
        else:
            print(f'Response: {mod_wlan.status_code}. CHANGE FAILED!')



    def get_wlan_auth(self, zone_id, wlan_id):
        """
        Use to retrieve wlan authentication profile info

        Parameters:
        zone_id - zone ID value
        wlan_id - WLAN ID value

        Returns:
        auth_profile_name - string
        """

        wlan_info = self.session.get(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/\
            wlans/{wlan_id}').json()

        auth_profile_name = wlan_info['authServiceOrProfile']['name']

        # Return authentication profile name
        return auth_profile_name



    #-----------------------------------------------------------
    # The METHODS below are for AP based activities!
    #-----------------------------------------------------------

    def apgroup_info(self, zone):
        """
        Info for an apgroup associated with the requested zone

        Parameters:
        zone - zone name

        Returns:
        """

        # Get zone_id
        zone_id = self.get_zone_id(zone)
        apgroup = self.session.get(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/apgroups').json()

        # Go over all AP Group lists
        for i in range(0,len(apgroup['list'])):
            # Get apgroup Id for each apgroup
            apgroup_id = apgroup['list'][i]['id']

            # Print apgroup detailed info
            print(self.session.get(f'{self.scg200_uri}/v5_0/rkszones/{zone_id}/apgroups\
                /{apgroup_id}').json())



    def ap_info(self, ap_mac):
        """
        Provide AP information

        Parameters:
        ap_mac - MAC address of the AP

        Returns:
        apinfo - string
        """

        return self.session.get(f'{self.scg200_uri}/v5_0/aps/{ap_mac}', verify=False).json()



    def ap_reboot(self, ap_macs):
        """
        Reboot a list of APs

        Parameters:
        ap_macs - list of APs MAC addresses

        Returns:
        """

        for ap_mac in ap_macs:
            ap_reboot = self.session.put(f'{self.scg200_uri}/v5_0/aps/{ap_mac}/reboot')

            print(ap_reboot)



    def ap_support_log(self, ap_mac):
        """
        Get support log info for an AP

        Parameters:
        ap_mac - MAC address of the AP of interest

        Returns:
        supportLog - string
        """

        # NOT WORKING YET!!

        return self.session.get(f'{self.scg200_uri}/v5_0/aps/{ap_mac}/supportLog')



    def ap_blink_led(self, ap_mac):
        """
        Blink LED to identify an AP from a group of APs installed

        Parameters:
        ap_mac - MAC address of the AP

        Returns:
        """

        self.session.post(f'{self.scg200_uri}/v5_0/aps/{ap_mac}/operational/blinkLed')




    #----------------------------------------------------------------------------------------
    # The METHOD below closes the Session you opened when you instantiate the Ruckus Object!
    #----------------------------------------------------------------------------------------

    def log_out(self):
        """
        Log out of the SCG200 API

        Parameters:

        Returns:
        """

        self.session.delete(f'{self.scg200_uri}/v5_0/session', verify=False)
