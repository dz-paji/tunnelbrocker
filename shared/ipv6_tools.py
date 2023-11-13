import ipaddress

def calculate_subnet(ipv6_address):
    '''
    Calculate the prefix and netmask of a given ipv6 prefix
    :param ipv6_address: ipv6 prefix
    :type string
    :return: prefix and netmask
    :rtype string, string
    '''
    ipv6 = ipaddress.IPv6Network(ipv6_address)
    prefix = ipv6.network_address
    netmask = ipv6.netmask
    return prefix, netmask
