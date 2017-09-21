import csv
import ipaddress
from flask import Flask, request
from flask_restful import Resource, Api
from flask import Response

app = Flask(__name__)
api = Api(app)


def resolv_geo_id(geoInfo , id):
    for row in geoInfo:
        if(row['geoname_id'] == id):
            return row['country_iso_code']
    return None

class Tree:
    val = None
    zero = None
    one = None
    def add(self, binip, country):
        if len(binip) == 0:
            self.val = country
        elif binip[0] == "0":
            if self.zero:
                self.zero.add(binip[1:],country)
            else:
                self.zero = Tree()
                self.zero.add(binip[1:],country)
        else:
            if self.one:
                self.one.add(binip[1:],country)
            else:
                self.one = Tree()
                self.one.add(binip[1:],country)
    def search(self, binip):
        if len(binip) == 0:
            return self.val
        if binip[0] == "0":
            if self.zero:
                return self.zero.search(binip[1:])
            else:
                return self.val
        else:
            if self.one:
                return self.one.search(binip[1:])
            else:
                return self.val

print("initialisation of ressource")
NetworkBLockIPv6 = Tree()
NetworkBLockIPv4 = Tree()
geoInfo = list(csv.DictReader(open("GeoLite2-Country-Locations-fr.csv", 'r'), delimiter=',', quotechar='"'))

tempNetworkBLockIPv6 = list(csv.DictReader(open("GeoLite2-Country-Blocks-IPv6.csv", 'r'), delimiter=',', quotechar='"'))
for block in tempNetworkBLockIPv6:
    iptochange = ipaddress.ip_network(block['network'])
    binip = bin(int(iptochange[0]))[2:]
    binip = binip[0:int(iptochange.prefixlen)]
    NetworkBLockIPv6.add(binip,resolv_geo_id(geoInfo, block["geoname_id"]))
tempNetworkBLockIPv6 = None
print("[*] IPv6 finised")

tempNetworkBLockIPv4 = list(csv.DictReader(open("GeoLite2-Country-Blocks-IPv4.csv", 'r'), delimiter=',', quotechar='"'))
for block in tempNetworkBLockIPv4:
    iptochange = ipaddress.ip_network(block['network'])
    binip = bin(int(iptochange[0]))[2:]
    binip = binip[0:int(iptochange.prefixlen)]
    NetworkBLockIPv4.add(binip,resolv_geo_id(geoInfo, block["geoname_id"]) )
tempNetworkBLockIPv4 = None 
print("[*] IPv4 finished")
geoInfo = None

class geoIP(Resource):

    def get(self,ip):
        ipObject = ipaddress.ip_address(ip)
        if ipObject.version == 4:
            biniptosearch = bin(int(ipObject))[2:]
            geoid = NetworkBLockIPv4.search(biniptosearch)
            return Response(geoid, mimetype='text/plain')
        else:
            biniptosearch = bin(int(ipObject))[2:]
            geoid = NetworkBLockIPv6.search(biniptosearch)
            return Response(geoid, mimetype='text/plain')

api.add_resource(geoIP, '/geo/<ip>')

if __name__ == '__main__':
     app.run(host= '0.0.0.0',port='5002')

