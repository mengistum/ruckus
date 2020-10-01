#!/usr/bin/env python

"""
Author:  Meheretab Mengistu
Purpose: To change Authentication Profile for SFUSD 802.1X
Version: 1.0
Date:    September 29, 2020
"""

# Import required modules
from getpass import getpass
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
    controller_ip = input('\nPlease enter the Controller IP: ')
    controller_port = input('\nPlease enter the Controller Port number: ')

    # Create a Ruckus object
    apr = Ruckus(controller_ip, controller_port, username, password)

    # Get all zones and their info
    # zones = apr.get_zones()['list']

    # Sample zones for testing purpose only!
    zones = [{'id': '3e366417-0d38-42c1-9ad7-75977bd3423d', 'name': '003-SCG-TEST'},  \
    {'id': '486b1c1d-2d87-439e-889d-88046db02bea', 'name': '001-NPS-Site'}, \
     {'id': '3e366417-0d38-42c1-9ad7-75977bd3423d', 'name': '003-SCG-TEST'}, \
     {'id': '606afd6f-ac14-4f29-8e36-62081aaade26', 'name': '004-Gill-TEST'}, \
      {'id': '6f13bca3-cf8f-4337-b744-6fa2a7c2161b', 'name': '002-ACS-Site'}, \
      {'id': '4bc42ffc-5ee9-45e6-8af3-933e35ec7fd4', 'name': '005-TestCert'}, \
       {'id': 'b344512f-1edc-4e6a-bc7a-5c642adebd65', 'name': '006-ISE-Site'}]

    # Print the list of zones to modify
    print(f'\n\nThe list of zones to modify:- \n\n\n {zones}')

    # Select whether you want to use the F5-VIP or NPS for authentication_profile
    auth_profile = input('\nPlease select either F5 or NPS for Authentication: [F5/NPS] ') or 'F5'

    if auth_profile.upper() == 'F5':
        auth_service_name = 'F5-VIP-ISE-Radius'
    else:
        auth_service_name = 'NPS-Radius-Proxy'


    # Open a file to write the resulting output
    with open('ise_transition_output.txt', 'w+') as out_file:

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
