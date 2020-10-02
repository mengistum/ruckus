#!/usr/bin/env python

"""
Author:  Meheretab Mengistu
Purpose: To change Authentication Profile for SFUSD 802.1X
Version: 2.0
Date:    October 02, 2020
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

    # Get all zones and their info
    # zones = apr.get_zones()['list']

    # Sample zones for testing purpose only!
    print("\nSample zones for TESTING PURPOSE ONLY. Comment out this section \
        starting this print statement until the beginning of the next print statement, \
        and Uncomment the line ** zones = apr.get_zones()['list'] ** to apply the \
        change to all zones in the controller!")
    zones = [{'id': '3e366417-0d38-42c1-9ad7-75977bd3423d', 'name': '003-SCG-TEST'},  \
    {'id': '486b1c1d-2d87-439e-889d-88046db02bea', 'name': '001-NPS-Site'}, \
     {'id': '3e366417-0d38-42c1-9ad7-75977bd3423d', 'name': '003-SCG-TEST'}, \
     {'id': '606afd6f-ac14-4f29-8e36-62081aaade26', 'name': '004-Gill-TEST'}, \
      {'id': '6f13bca3-cf8f-4337-b744-6fa2a7c2161b', 'name': '002-ACS-Site'}, \
      {'id': '4bc42ffc-5ee9-45e6-8af3-933e35ec7fd4', 'name': '005-TestCert'}, \
       {'id': 'b344512f-1edc-4e6a-bc7a-5c642adebd65', 'name': '006-ISE-Site'}]

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
            print(f'{auth_profile} is wrong choice. Please enter correct choice!')

    # Create a filename by using modified current time
    #   Get current time and modify it by replacing ":" with ""
    modified_time = datetime.now().isoformat(timespec='seconds').replace(':', '')
    #   Create a new output file
    filename = f'ise_transition_ouptput_{modified_time}.txt'

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


if __name__ == "__main__":

    main()

    input('\nPress any key to exit!')
