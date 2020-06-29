## --------------------------------------------------------- ##
##                       dataReader.py                       ##
##                                                           ##
## Script to read volume-format binary files from NGA        ##
## Author: Jonathan F. MacArt                                ##
## Date:   3 October 2018                                    ##
## --------------------------------------------------------- ##

import sys
import numpy as np
import struct
import array as arr
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#from mpi4py import MPI


def plotData(data,fName):
    # Plot 2D data
    fig = plt.figure(figsize=(6,3))
    plt.imshow(data.astype(np.float64), interpolation='nearest', cmap=cm.gist_rainbow)
    plt.colorbar()
    fig.tight_layout()
    fig.savefig(fName+".png", format="png")
    plt.close(fig)
    


# --------------------------------------------------------
# Read state data from a RESTART format data file
# --------------------------------------------------------    
def readNGArestart(fName,readData=True):

    f = open(fName, 'rb')
    
    # Read data sizes
    f_Data = f.read(16)
    nx     = struct.unpack('<i',f_Data[ 0: 4])[0]
    ny     = struct.unpack('<i',f_Data[ 4: 8])[0]
    nz     = struct.unpack('<i',f_Data[ 8:12])[0]
    nvar   = struct.unpack('<i',f_Data[12:16])[0]
    
    # Read timestep size and simulation time
    f_Data = f.read(16)
    dt     = struct.unpack('<d',f_Data[0:8])[0]
    time   = struct.unpack('<d',f_Data[8:16])[0]
    
    # Read names of the variables in the file
    f_Data = f.read(8*nvar)
    names  = ['']*nvar
    for ivar in range(nvar):
        nameStr = struct.unpack("cccccccc",f_Data[ivar*8:(ivar+1)*8])
        for s in nameStr:
            if (s.isspace())==False:
                names[ivar] += s.decode('UTF-8')
        
    # Print some file info
    #if (True):
    #    print(' ')
    #    print(fName)
    #    print('   Data file at time: {}'.format(time))
    #    print('   Timestep size:     {}'.format(dt))
    #    print('   Number of vars:    {}'.format(nvar))
    #    print('   Variables in file: {}'.format(names))

    if readData:
        # Read data arrays in serial and return the output
        nread = nvar
        #nread = min([31,nvar])
        data   = np.empty([nx,ny,nz,nread])
        for ivar in range(nread):
            inData = arr.array('d')
            inData.fromfile(f, nx*ny*nz)
            data[:,:,:,ivar] = np.frombuffer(inData,dtype='f8').reshape((nx,ny,nz),order='F')
            #print('   --> Done reading {}'.format(names[ivar]))
            
        #print(data.shape)
        #plotData(data[:,:,int(nz/2),0],"test")

        return(names,data)

    else:
        # Just return the grid info and variable names
        # Need to call readNGA_parallel to get data
        return(names)


# --------------------------------------------------------
# Read the grid and data from a VOLUME format data file
# --------------------------------------------------------
def readNGA(fName,readData=True):

    f = open(fName, 'rb')
    
    # Read data sizes
    f_Data = f.read(20)
    ntime  = struct.unpack('<i',f_Data[ 0: 4])[0]
    nx     = struct.unpack('<i',f_Data[ 4: 8])[0]
    ny     = struct.unpack('<i',f_Data[ 8:12])[0]
    nz     = struct.unpack('<i',f_Data[12:16])[0]
    nvar   = struct.unpack('<i',f_Data[16:20])[0]
    
    # Read grid coordinates in x, y, z
    xGrid = arr.array('d')
    xGrid.fromfile(f, nx)
    
    yGrid = arr.array('d')
    yGrid.fromfile(f, ny)
    
    zGrid = arr.array('d')
    zGrid.fromfile(f, nz)
    
    # Read names of the variables in the file
    f_Data = f.read(8*nvar)
    names  = ['']*nvar
    for ivar in range(nvar):
        nameStr = struct.unpack("cccccccc",f_Data[ivar*8:(ivar+1)*8])
        for s in nameStr:
            if (s.isspace())==False:
                names[ivar] += s.decode('UTF-8')
    
    # Read timestep size and simulation time
    f_Data = f.read(16)
    dt     = struct.unpack('<d',f_Data[0:8])[0]
    time   = struct.unpack('<d',f_Data[8:16])[0]
        
    # Print some file info
    #if (0):
    #    print(' ')
    #    print(fName)
    #    print('   Grid size:         nx={}, ny={}, nz={}'.format(nx,ny,nz))
    #    print('       xmin, xmax:    {}, {}'.format(min(xGrid),max(xGrid)))
    #    print('       ymin, ymax:    {}, {}'.format(min(yGrid),max(yGrid)))
    #    print('       zmin, zmax:    {}, {}'.format(min(zGrid),max(zGrid)))
    #    print('   Data file at time: {}'.format(time))
    #    print('   Timestep size:     {}'.format(dt))
    #    print('   Number of vars:    {}'.format(nvar))
    #    print('   Variables in file: {}'.format(names))
    
    xGridOut = np.frombuffer(xGrid,dtype='f8')
    yGridOut = np.frombuffer(yGrid,dtype='f8')
    zGridOut = np.frombuffer(zGrid,dtype='f8')

    if readData:
        # Read data arrays in serial and return the output
        nread = nvar
        #nread = min([31,nvar])
        data   = np.empty([nx,ny,nz,nread])
        for ivar in range(nread):
            inData = arr.array('d')
            inData.fromfile(f, nx*ny*nz)
            data[:,:,:,ivar] = np.frombuffer(inData,dtype='f8').reshape((nx,ny,nz),order='F')
            #print('   --> Done reading {}'.format(names[ivar]))
            
        #print(data.shape)
        #plotData(data[:,:,int(nz/2),0],"test")

        return(names,data)
        #return(xGridOut,yGridOut,zGridOut,names,data)

    else:
        # Just return the grid info and variable names
        # Need to call readNGA_parallel to get data
        return(xGridOut,yGridOut,zGridOut,names,time)


    


