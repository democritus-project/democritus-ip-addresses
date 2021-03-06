import ipaddress
import re
from functools import partial
from typing import Iterable

from d8s_csv import csv_read_as_dict
from d8s_hypothesis import hypothesis_get_strategy_results
from d8s_networking import get
from hypothesis.strategies._internal.ipaddress import ip_addresses
from ioc_finder import ioc_finder


def ipv4_address_examples(n: int = 10):
    """Create n ipv4 addresses."""
    ipv4_addresses_func = partial(ip_addresses, v=4)

    return hypothesis_get_strategy_results(ipv4_addresses_func, n=n)


def ipv6_address_examples(n: int = 10):
    """Create n ipv6 addresses."""
    ipv6_addresses_func = partial(ip_addresses, v=6)

    return hypothesis_get_strategy_results(ipv6_addresses_func, n=n)


def ipv4_addresses_find(text):
    """Parse IPv4 addresses from the given text."""
    return ioc_finder.parse_ipv4_addresses(text)


def ipv6_addresses_find(text):
    """Parse IPv6 addresses from the given text."""
    return ioc_finder.parse_ipv6_addresses(text)


def ip_addresses_find(text):
    """Parse ip addresses from the given text."""
    results = []
    results.extend(ipv4_addresses_find(text))
    results.extend(ipv6_addresses_find(text))
    return results


def ip_is_private(ip):
    """Check if the IP address is private."""
    return ipaddress.ip_address(ip).is_private


def ip_is_multicast(ip):
    """Check if the IP address is multicast."""
    return ipaddress.ip_address(ip).is_multicast


def ip_is_public(ip):
    """Check if the IP address is public (i.e. not reserved and not multicast)."""
    ip = ipaddress.ip_address(ip)
    return not ip.is_multicast and not ip.is_private


def is_ip_address(text):
    """Determine whether or not the given text is an ip address."""
    try:
        ipaddress.ip_address(text)
    except ValueError:
        return False
    else:
        return True


def ip_whois(ip):
    """Get whois information for the given ip address."""

    return get(f'https://ipapi.co/{ip}/json/', process_response=True)


def ip_is_reserved(ip):
    """Check if the IP address is IETF (https://www.ietf.org/) reserved."""
    return ipaddress.ip_address(ip).is_reserved


def ip_version(ip):
    """Get the version number of the ip address (4 or 6)."""
    return ipaddress.ip_address(ip).version


def ip_network_block_first_address(network_block: str):
    """Return the first address of the given network_block."""
    # TODO: this function could also be called "ipNetworkBlockNetworkAddress"
    ip_network = ipaddress.ip_network(network_block)
    return str(ip_network.network_address)


def ip_network_block_last_address(network_block: str):
    """Return the first address of the given network_block."""
    # TODO: this function could also be called "ipNetworkBlockBroadcastAddress"
    ip_network = ipaddress.ip_network(network_block)
    return str(ip_network.broadcast_address)


def ip_network_block_ip_count(network_block_string):
    """Get the number of IP addresses in the given network block."""
    return ipaddress.ip_network(network_block_string).num_addresses


def ip_network_block_to_range(network_block_string):
    """Return the range of IP addresses covered by the network block in the form "<starting-ip> - <ending-ip>"."""
    ip = ipaddress.ip_network(network_block_string)
    return '{} - {}'.format(ip.network_address, ip.broadcast_address)


def ip_network_block_enumerate(network_block_string) -> Iterable[str]:
    """Yield all of the ip addresses in the given network_block_string."""
    ip = ipaddress.ip_network(network_block_string)

    # we yield the `network_address` and the `broadcast_address` because these are not included in the ip.hosts()...
    # function (see https://docs.python.org/3/howto/ipaddress.html#inspecting-address-network-interface-objects)
    yield str(ip.network_address)
    yield from (str(ip) for ip in ip.hosts())
    yield str(ip.broadcast_address)


def ip_in_network_block(ip_address: str, network_block: str):
    """Return whether or not the given ip_address is in the network_block."""
    addresses = ip_network_block_enumerate(network_block)
    result = ip_address in addresses
    return result


def ip_range_to_network_block(ip_range_string):
    """Take a range like "<starting-ip> - <ending-ip>" and convert this into an IP address network block."""
    # pattern = r'(\S*) ?- ?(\S*)'
    # results = re.findall(pattern, ip_range_string)
    # return ???
    raise NotImplementedError


def ipv6_expand(ip_v6):
    """Expand (also known as 'Exploding') an ipv6 address."""
    return ipaddress.IPv6Address(ip_v6).exploded


def ipv6_compress(ip_v6):
    """Compress an ipv6 address."""
    return ipaddress.IPv6Address(ip_v6).compressed


def ipv6_threatconnect_form(ip_v6):
    """Format ipv6 address as expected by ThreatConnect."""
    address_sections = [section.replace("0000", "xxxx").lstrip("0") for section in ipv6_expand(ip_v6).split(":")]
    formatted_address_sections = ":".join(address_sections)
    return formatted_address_sections.replace("xxxx", "0")


def ip_current():
    """Get the current ip address."""

    return get('https://ipinfo.io/json', process_response=True)


def ipv4_private_addresses():
    """Get private ipv4 addresses.

    Data from: https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml."""  # noqa: E501
    private_ipv4_addresses = csv_read_as_dict(
        get(
            'https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry-1.csv',
            process_response=True,
        )
    )
    return private_ipv4_addresses


def ipv6_private_addresses():
    """Get private ipv6 addresses.

    Data from: https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml#iana-ipv6-special-registry-1."""  # noqa: E501
    private_ipv6_addresses = csv_read_as_dict(
        get(
            'https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry-1.csv',
            process_response=True,
        )
    )
    return private_ipv6_addresses


def ipv4_sum(ipv4_address):
    """Find the sum of the ip address by adding each section of the ip address.

    For example, 8.8.8.8 would sum to 32 (calculated by taking 8 + 8 + 8 + 8).
    """
    return sum([int(i) for i in ipv4_address.split('.')])


def ipv4_is_possible_version_number(ipv4_address):
    """Determine whether or not the ipv4 ip address is likely a version number or not.

    This is a beta function and is a work in progress.
    The word "Possible" in the function name should be taken seriously -
    this function will return `True` if the ipv4_address *might* be a version number.
    The results of this function are conjecture and should not be used definitively.
    """
    # if the ipv4_address starts with a number followed by `.0.`, we can assume it is a version number
    pattern = r'(?<![0-9.])[0-9]{1,2}\.[0-2]\.'
    if re.findall(pattern, ipv4_address):
        return True

    # if the sum of the numbers that make up the ip address are not sufficiently large...
    # it is possible that this ip address is a version number
    if ipv4_sum(ipv4_address) < 30:
        return True

    return False
