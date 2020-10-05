#!/usr/bin/env python

"""
Author:  Meheretab Mengistu
Purpose: To change Authentication Profile for SFUSD 802.1X
Version: 3.0
Date:    October 05, 2020
"""

# Import required modules
from getpass import getpass
from datetime import datetime
from ruckus import Ruckus



# Get Credentials
def get_credentials():
    """
    Get username and password

    Parameters:

    Returns:
    username - string
    password - string
    """
    username = input('\nPlease enter username: ')
    password = getpass()

    return username, password


def group_zones(all_zones, zone_grp):
    """
    Used to group zones in to different zone groups

    Parameters:
    all_zones - all zones in the controller
    zone_grp - user choice of a zone group

    Returns:
    zones - list of zones of one zone group
    """

    # Create empty lists for CDC(EES), ES, MS, HS, Office, and Test Zones
    zones_cdc = []
    zones_es = []
    zones_ms = []
    zones_hs = []
    zones_office = []
    zones_test = []

    # Splitting all zones in to different group of zones
    for site in all_zones:
        zone_name = site['name']
        if zone_name.startswith('CDC-'):
            zones_cdc.append(site)
        if zone_name.startswith('ES-'):
            zones_es.append(site)
        elif zone_name.startswith('MS-'):
            zones_ms.append(site)
        elif zone_name.startswith('HS-'):
            zones_hs.append(site)
        elif zone_name.startswith('OFC-'):
            zones_office.append(site)
        elif zone_name.startswith('00'):
            zones_test.append(site)

    # Use zone_grp provided to return zones of user choice
    if zone_grp.upper() == 'CDC':
        zones = zones_cdc
    elif zone_grp.upper() == 'ES':
        zones = zones_es
    elif zone_grp.upper() == 'MS':
        zones = zones_ms
    elif zone_grp.upper() == 'HS':
        zones = zones_hs
    elif zone_grp.upper() == 'OFC':
        zones = zones_office
    elif zone_grp.upper() == 'TEST':
        zones = zones_test
    else:
        zones = all_zones

    # Return zones
    return zones



def main():
    """
    This will be the main function
    """
    username, password = get_credentials()

    # Request controller_ip and controller_port
    controller_ip = input('\nPlease enter the Controller IP (ONLY IP address): ')
    controller_port = input('\nPlease enter the Controller Port number: ')

    # Create a Ruckus object
    apr = Ruckus(controller_ip, controller_port, username, password)

    # Get all zones on the controller and their info
    all_zones = apr.get_zones()['list']

    # Create a while loop to allow to continue working on more zone groups
    #  create a variable named 'proceed' to ask the user whether to proceed
    proceed = True

    while proceed:

        print('\n You can work on one group of zones at a time (to be safe). Please select \n  \
"CDC" for CDCs (Early Education Schools),\n  "ES" for Elementary School Zones,\n  \
"MS" for Middle School Zones,\n  "HS" for High School Zones,\n  "OFC" for Office Zones,\n  \
"Test" for Test Zones,\n  "ALL" to work on all zones\n')

        zone_grp = input('Please select which zones to modify [ CDC | ES | MS | HS | OFC | Test | \
ALL ]: ') or 'Test'

        # Call group_zones function to get zones to modify
        zones = group_zones(all_zones, zone_grp)
        # Print the list of zones to modify
        print(f'\n\nThe list of zones to modify:- \n\n\n {zones}')

        # A loop to make sure the user selects either F5 or NPS
        while True:
            # Select whether you want to use the F5-VIP or NPS for authentication_profile
            auth_profile = input('\nPlease enter either F5 or NPS for Authentication: [F5/NPS] ')\
             or 'F5'
            if auth_profile.upper() == 'F5':
                auth_service_name = 'F5-VIP-ISE-Radius'
                break
            elif auth_profile.upper() == 'NPS':
                auth_service_name = 'NPS-Radius-Proxy'
                break
            else:
                print(f'{auth_profile} is WRONG choice. Please enter correct choice!')

        # Create a filename by using modified current time
        #   Get current time and modify it by replacing ":" with ""
        modified_time = datetime.now().isoformat(timespec='seconds').replace(':', '')
        #   Create a new output file
        filename = f'ise_transit_{zone_grp}_{modified_time}.txt'

        # Open the file to write the resulting output
        with open(filename, 'w+') as out_file:
            # Work on each site or zone
            for site in zones:
                zone_id = site['id']
                # Get WLAN ID for each zone and print zone_name with wlan_id
                wlan_id = apr.get_wlan_id(zone_id)
                print(f"\n{site['name']} ... wlan_id = {wlan_id}")
                out_file.write(f"\n{site['name']} ... wlan_id = {wlan_id}")
                # If wlan Id is '0', there is no "SFUSD" SSID. Escape the rest of the codes.
                if wlan_id == '0':
                    continue
                # Get and print the Authentication Profile for the site
                auth_profile_name = apr.get_wlan_auth(zone_id, wlan_id)
                print(f"Before Change:- Auth_profile for *** {site['name']} *** is *** \
                {auth_profile_name}")
                out_file.write(f"\nBefore Change:- Auth_profile for *** {site['name']} *** is *** \
                {auth_profile_name}")
                # Modify the authentication profile for the SSID
                apr.modify_wlan_auth(zone_id, wlan_id, auth_service_name)
                # Get and print the Authentication Profile for the site
                auth_profile_name = apr.get_wlan_auth(zone_id, wlan_id)
                print(f"After Change:- Auth_profile for *** {site['name']} *** is *** \
                {auth_profile_name}\n")
                out_file.write(f"\nAfter Change:- Auth_profile for *** {site['name']} *** is *** \
                    {auth_profile_name}\n")

        choice = input('\nDo you want to work on more zone groups? [Y|N]: ') or 'N'
        if choice.upper() == 'Y':
            proceed = True
        else:
            proceed = False


if __name__ == "__main__":

    main()

    input('\nPress any key to exit!')
