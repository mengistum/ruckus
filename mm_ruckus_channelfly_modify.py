#!/usr/bin/env python

"""
Author:  Meheretab Mengistu
Purpose: To change AP Login information
Version: 1.1
Date:    March 26, 2021
"""

# Import required modules
from datetime import datetime
from ruckus import Ruckus
from mm_common_funcs import get_credentials, group_zones


def main():
    """
    This will be the main function
    """
    print('\n******* This script will Turn ON/OFF ChannelFly per zone ********\n\n')

    # Get username and password
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

        # Create a filename by using modified current time
        #   Get current time and modify it by replacing ":" with ""
        modified_time = datetime.now().isoformat(timespec='seconds').replace(':', '')
        #   Create a new output file
        filename = f'channelfly_modified_{zone_grp.upper()}_{modified_time}.txt'

        # Ask whether do you want to turn off channelfly
        print('\n\nDo you want to DISABLE ChannelFly? Choose Y(Yes), N(No), B(BackgroundScanning):')
        turn_off = input('(Y/B/N):  ') or 'Y'
        # Ask which channel to work on
        channel = input('Which channel do you want to work on (both/2.4/5.0):  ') or 'both'

        # Open the file to write the resulting output
        with open(filename, 'w+') as out_file:
            # Prepare headers for the output file
            out_file.write("\n--------------------------------------------------------\n")
            out_file.write("{0:40} {1:>5}".format("ZONE", "STATUS CODE"))
            out_file.write("\n--------------------------------------------------------\n")
            # Work on each site or zone
            for site in zones:
                # Call the function to TURN ON/OFF ChannelFly
                response = apr.channelfly(site['id'], turn_off, channel)
                out_file.write("{0:40} {1:>5}\n".format(site['name'], response.status_code))


        print('\nIf you want to work on more zone groups, press ANY KEY! Otherwise, press ENTER! ')
        proceed = bool(input(' ') or None)


if __name__ == "__main__":

    main()

    input('\nPress any key to exit!')
