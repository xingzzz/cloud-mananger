class Hardware:
    """
    This is the class that used to represent one physical machines

    Attributes:
        name (str): name of the server
        rackName (str): name of the rack
        ip (str): IP address of the server
        memSize (int): amount of RAM in GB
        numDisk (int): number of virtual disks the machine can accommodate locally
        numVcpu (int): number of virtual CPUs cores that the hardware can accommodate
    """

    def __init__(self, name, rackName, ip, memSize, numDisk, numVcpu):
        """
        constructor of Hardware class

        Args:
            name (str): name of the server
            rackName (str): name of the rack
            ip (str): IP address of the server
            memSize (int): amount of RAM in GB
            numDisk (int): number of virtual disks the machine can accommodate locally
            numVcpu (int): number of virtual CPUs cores that the hardware can accommodate
            instanceList (list): list of instance the current hardware is hosting
        """
        # hardware information
        self.name = name
        self.rackName = rackName
        self.ip = ip
        self.memSize = memSize
        self.numDisk = numDisk
        self.numVcpu = numVcpu

        # remain capacity for mem, disk, vcpus
        self.remainMem = memSize
        self.remainDisk = numDisk
        self.remainVcpu = numVcpu
        self.instanceList = []

    def show(self):
        """
        show hardware specs
        """
        print " name: %s\n rackName: %s\n ip: %s\n mem: %d\n num-disks: %d\n num-vcpus: %d\n" \
              % (self.name, self.rackName, self.ip, self.memSize, self.numDisk, self.numVcpu)

    def showRemainCapacity(self):
        """
        show remain capacity
        """
        print "available mem: %d\n available num-disks: %d\n available num-vcpus: %d\n" \
              % (self.remainMem, self.remainDisk, self.remainVcpu)

    def canHost(self, flavor):
        """
        check if the hardware can host the instance with spec
        """
        if self.remainMem >= flavor.memSize \
            and self.remainDisk >= flavor.numDisk \
            and self.remainVcpu >= flavor.numVcpu:
            return True

        return False

    def host(self, instance):
        """
        host a instance
        """
        self.remainMem -= instance.flavor.memSize
        self.remainDisk -= instance.flavor.numDisk
        self.remainVcpu -= instance.flavor.numVcpu
        self.instanceList.append(instance)
        return True

    def remove(self, instName):
        """
        remove a instance
        """
        for instance in self.instanceList:
            if instance.name == instName:
                self.remainMem += instance.flavor.memSize
                self.remainDisk += instance.flavor.numDisk
                self.remainVcpu += instance.flavor.numVcpu
                self.instanceList.remove(instance)
                return True
        print "No instance %s found in hardware %s" % (instName, self.name)
        return False

    def getInstanceList(self):
        """
        remove a instance
        """
        return self.instanceList