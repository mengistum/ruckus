#!/usr/bin/env python

"""
Author:  Meheretab Mengistu
Purpose: To change AP Login information
Version: 1.0
Date:    March 22, 2021
"""

# Import required modules
from datetime import datetime
from ruckus import Ruckus
from mm_common_funcs import get_credentials, group_zones


def main():
    """
    This will be the main function
    """
    print('\n******* This script will change the AP Login password per zone ********\n\n')

    # Get username and password
    username, password = get_credentials()

    # Request controller_ip and controller_port
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
        filename = f'aplogin_modified_{zone_grp.upper()}_{modified_time}.txt'

        # Get the new password from the user and create a dictionary
        ap_password = input('\n\nPlease enter the new password for the APs. \
            Check with Ruckus documentation on password requirements: ')
        aplogin = {'apLoginName':'admin', 'apLoginPassword':ap_password}

        # Open the file to write the resulting output
        with open(filename, 'w+') as out_file:
            # Work on each site or zone
            for site in zones:
                # Call the function to change APs login password
                response = apr.update_ap_login(site['id'], aplogin)
                # If the change is successful
                if response == 204:
                    out_file.write(f"{site['name']} ---- AP Login is SUCCESSFULLY CHANGED!\n\n")
                else:
                    out_file.write(f"{site['name']} ---- Username/password change FAILED!\n\n")


        print('\nIf you want to work on more zone groups, press any key! Otherwise, press Enter! ')
        proceed = bool(input(' ') or None)


if __name__ == "__main__":

    main()

    input('\nPress any key to exit!')
