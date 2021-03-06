from Config import LOGGER_NAME
from hardware.Hardware import Hardware
from hardware.Rack import Rack

import logging


class HardwareManager:
    """
    HardwareManager class will contains all hardware information and status for AggieStack

    Attributes:
        hardwareDict (list): list for all Hardware
        rackDict (list): list for all Hardware
        numHardware (int): numbers of hardware in current AggieStack
        numRack (int): numbers of rack in current AggieStack
    """

    def __init__(self):
        """
        constructor of HardwareManager class
        """
        self.hardwareDict = {}
        self.rackDict = {}
        self.numHardware = 0
        self.numRack = 0
        self.logger = logging.getLogger(LOGGER_NAME)

    def addHardware(self, fname):
        """
        Added a list of rack from a configuration file
        Added a list of hardware from a configuration file

        Args:
            fname (str): name of the file to read the configuration
        """
        try:
            with open(fname, 'r') as f:
                lines = f.readlines()
                self.numRack = int(lines[0])
                racks = lines[1:self.numRack + 1]
                for rack in racks:
                    tokens = rack.split(" ")
                    self.rackDict[tokens[0]] = Rack(name=tokens[0],
                                                    capacity=int(tokens[1]))

                self.numHardware = int(lines[self.numRack + 1])
                hardwares = lines[self.numRack + 2:]
                for hardware in hardwares:
                    tokens = hardware.split(" ")
                    self.hardwareDict[tokens[0]] = Hardware(name=tokens[0],
                                                            rackName=tokens[1],
                                                            ip=tokens[2],
                                                            memSize=int(tokens[3]),
                                                            numDisk=int(tokens[4]),
                                                            numVcpu=int(tokens[5]))
            f.close()

        except Exception as e:
            self.logger.exception(e)
            return False

        return True

    def addHardwareAdmin(self, command):
        """
        Added the machine to the system so that it may receive new instances.
        This is usually invoked when a "sick" server was fixed, and it is ready to work again.

        Args:
            command (list): --mem MEM --disk NUM_DISKS --vcpus VCPUs  --ip IP rack RACK_NAME MACHINE
        """

        if command[9] in self.rackDict:
            if command[10] not in self.hardwareDict:
                self.hardwareDict[command[10]] = Hardware(name=command[10],
                                                    rackName=command[9],
                                                    ip=command[7],
                                                    memSize=int(command[1]),
                                                    numDisk=int(command[3]),
                                                    numVcpu=int(command[5]))
                return True
            else:
                print "Hardware %s has already existed in hardware manager" % command[10]
                return False
        else:
            print "No rack %s in hardware manager" % command[9]
            return False

    def remove(self, name):
        """
        Removed hardware from a rack

        """
        if name in self.hardwareDict:
            del self.hardwareDict[name]
            return True
        return False

    def show(self):
        """
        Display information about the hardware hosting the cloud
        """
        print "======================================== Rack List ========================================"
        for key in self.rackDict:
            print "Rack name: %s" % key
            print "Rack remain capacity: %d" % self.rackDict[key].remainCap

        print "======================================== Hardware List ========================================"
        for key in self.hardwareDict:
            print "Hardware name: %s" % key
            self.hardwareDict[key].show()
        return True

    def showRemainCapacity(self):
        """
        show remainCapacity for all hardware
        """
        print "============================== Remaining Hardware Capacity List =============================="
        for key in self.hardwareDict:
            print "Hardware name: %s" % key
            self.hardwareDict[key].showRemainCapacity()
        return True

    def removeInstance(self, instName, serverName):
        """
        remove instance from a specific hardware
        """
        if serverName in self.hardwareDict:
            return self.hardwareDict[serverName].remove(instName)
        else:
            print "No hardware %s in hardware manager" % serverName
            return False

    def priorHost(self, image, flavor):
        """
        prioritize server where the required image is already cached,
        or one rack with more free space,
        or choose one rack to remove an image

        Args:
            image (image)
            flavor (flavor)
        """
        rackList = sorted(self.rackDict.values(), key=lambda x: x.remainCap, reverse=True)


        for rack in rackList:
            imgCached = False
            for localImage in rack.imageDict.keys():
                if localImage == image.name:
                    imgCached = True
                    break
            if imgCached:
                for hardware in self.hardwareDict.keys():
                    if self.hardwareDict[hardware].canHost(flavor) and \
                            self.hardwareDict[hardware].rackName == rack.name:
                        return hardware
            # if rack.remainCap > maxSpace and\
            #         rack.canHost(image):
            #     maxSpace = self.rackDict[rack].remainCap
            #     rackWithSpace = rack
        for rack in rackList:
            for hardware in self.hardwareDict.keys():
                if self.hardwareDict[hardware].canHost(flavor) and \
                        rack.canHost(image):
                    rack.host(image)
                    return hardware

        for hardware in self.hardwareDict.keys():
            if self.hardwareDict[hardware].canHost(flavor):
                rack = self.hardwareDict[hardware].rackName
                for img in self.rackDict[rack].imageDict.keys():
                    self.rackDict[rack].remove(img)
                    if self.rackDict[rack].canHost(image):
                        self.rackDict[rack].host(image)
                        break
                return hardware
        print "No hardware is qualified"
        return False

    def showImageList(self, name):
        """
        lists the names of the images present in the specified rack
        and the amount available in the rack storage to host more image files

        Args:
            name (str): name of that rack
        """
        print "======================================== Image List of the Rack ========================================"
        print "Rack name: %s" % name
        list = self.rackDict[name].imageDict
        for key in list:
            print "Image name: %s" % key
        print "Rack remain capacity: %d" % self.rackDict[name].remainCap
        return True

