import ipaddress
import logging
from shared.InvalidSrcException import InvalidSrcException
from shared.InvalidEndpointException import InvalidEndpointException

class PacketFilter:
    def __init__(self) -> None:
        
        
        self.allocations = {}
        
        self.update_allocation()
        self.logger = logging.getLogger("packet_filter")
        
    def validate_src(self, prefix_v6) -> bool:
        '''
        validate the source address not from reserved ipv6 address range
        '''
        invalid_addresses = ["FF00::/8", "::1", "::FFFF:0:0/96"]
        rfc3513_addresses = "::/96"
        for address in invalid_addresses:
            if ipaddress.ip_address(prefix_v6).subnet_of(ipaddress.ip_network(address)):
                self.logger.error("source ipv6 address is invalid")
                raise InvalidSrcException("source ipv6 address is invalid")        
        
        if ipaddress.ip_address(prefix_v6).subnet_of(ipaddress.ip_network(rfc3513_addresses)):
            if not ipaddress.ip_address(prefix_v6).subnet_of(ipaddress.ip_network("::/128")):
                self.logger.error("source ipv6 address lies in RFC3513 range but not ::/128")
                raise InvalidSrcException("source ipv6 address lies in RFC3513 range but not ::/128")
            
        return True

        
    def validate_configured(self, prefix_v6, endpoint_v4) -> bool:
        '''
        Validate if the given prefix belongs to any configured tunnel
        :param prefix_v6: ipv6 prefix to be tested
        :type string
        :return: True if valid
        '''
        prefix_v6 = ipaddress.ip_network(prefix_v6)
        #TODO： rewrite with dict.get()
        for i in self.allocations:
            if prefix_v6.subnet_of(ipaddress.ip_network(i)):
                if self.allocations[i] == endpoint_v4:
                    return True
                else:
                    raise InvalidEndpointException("Endpoint does not match with its prefix")
        
        raise InvalidEndpointException("Prefix not found")
    
    def validate(self, prefix_v6, endpoint_v4) -> bool:
        try:
            self.validate_configured(prefix_v6, endpoint_v4)
            self.validate_src(prefix_v6)
        except:
            return False
        
        return True
        
    def update_allocation(self):
        allocation_file = open("config/allocation.conf", "r")
        for i in allocation_file:
            if i.startswith("#"):
                continue

            this_prefix_v6 = i.split(" - ")[0]
            this_endpoint_v4 = i.split(" - ")[1].strip()
            self.allocations.update({this_prefix_v6: this_endpoint_v4})
            
    def endpoint_update(self, prefix_v6, endpoint_v4) -> bool:
        '''
        Update tunnel information from heartbeat
        '''
        
        prefix_v6 = ipaddress.ip_network(prefix_v6)\
            
        if self.allocations.get(prefix_v6) is not None:
            self.allocations.update({prefix_v6: endpoint_v4})
        
            return
                    
        raise InvalidEndpointException("Prefix not found")
                        
    def lookup_endpoint(self, prefix_v6) -> str:
        query_prefix_v6 = ipaddress.ip_network(prefix_v6)
        #TODO： rewrite with dict.get()
        for i in self.allocations:
            # self.logger.debug("lookup endpoint for %s against %s", query_prefix_v6, ipaddress.ip_network(i))
            if query_prefix_v6.subnet_of(ipaddress.ip_network(i)):
                return self.allocations[i]
            
        raise InvalidEndpointException("Prefix not found")
    
if __name__ == "__main__":
    print(True and False)