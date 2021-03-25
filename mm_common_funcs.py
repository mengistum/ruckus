#!/usr/bin/env python

"""
Author:  Meheretab Mengistu
Purpose: Common functions shared between other scripts for Ruckus automation
Version: 1.0
Date:    March 25, 2021
"""

# Import required modules
from getpass import getpass


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


# Group all zones to either CDC(EES), ES, MS, HS, Office, and/or Test Zones
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
