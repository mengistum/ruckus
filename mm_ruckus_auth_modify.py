#!/usr/bin/env python

"""
Author:  Meheretab Mengistu
Purpose: To change Authentication Profile for SFUSD 802.1X
Version: 3.1
Date:    March 25, 2021
"""

# Import required modules
from datetime import datetime
from ruckus import Ruckus
from mm_common_funcs import get_credentials, group_zones


def main():
    """
    This will be the main function
    """
    username, password = get_credentials()

    # Request controller_ip
    controller_ip = input('\nPlease enter the Controller IP (ONLY IP address): ')

    # Create a Ruckus object
    apr = Ruckus(controller_ip, username, password)

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
        filename = f'ise_transit_{zone_grp.upper()}_{modified_time}.txt'

        # Open the file to write the resulting output
        with open(filename, 'w+') as out_file:
            # Work on each site or zone
            for site in zones:
                # Get WLAN ID for each zone and print zone_name with wlan_id
                wlan_id = apr.get_wlan_id(site['id'])
                print(f"\n{site['name']} ... wlan_id = {wlan_id}")
                out_file.write(f"\n{site['name']} ... wlan_id = {wlan_id}")
                # If wlan Id is '0', there is no "SFUSD" SSID. Escape the rest of the codes.
                if wlan_id == '0':
                    continue
                # Get and print the Authentication Profile for the site
                auth_profile_name = apr.get_wlan_auth(site['id'], wlan_id)
                print(f"Before Change:- Auth_profile for *** {site['name']} *** is *** \
                {auth_profile_name}")
                out_file.write(f"\nBefore Change:- Auth_profile for *** {site['name']} *** is *** \
                {auth_profile_name}")
                # Modify the authentication profile for the SSID
                apr.modify_wlan_auth(site['id'], wlan_id, auth_service_name)
                # Get and print the Authentication Profile for the site
                auth_profile_name = apr.get_wlan_auth(site['id'], wlan_id)
                print(f"After Change:- Auth_profile for *** {site['name']} *** is *** \
                {auth_profile_name}\n")
                out_file.write(f"\nAfter Change:- Auth_profile for *** {site['name']} *** is *** \
                    {auth_profile_name}\n")


        print('\nIf you want to work on more zone groups, press ANY KEY! Otherwise, press ENTER! ')
        proceed = bool(input(' ') or None)



if __name__ == "__main__":

    main()

    input('\nPress any key to exit!')
