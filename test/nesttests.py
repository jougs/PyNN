"""
Unit tests for pyNN/nest.py.
$Id$
"""

import pyNN.nest as nest
import pyNN.common as common
import pyNN.random as random
import unittest
import numpy


# ==============================================================================
class CreationTest(unittest.TestCase):
    """Tests of the create() function."""
    
    def setUp(self):
        nest.setup()
    
    def tearDown(self):
        pass
    
    def testCreateStandardCell(self):
        """create(): First cell created should have GID==1"""
        ifcell = nest.create(nest.IF_curr_alpha)
        assert ifcell == 1, 'Failed to create standard cell'
        
    def testCreateStandardCells(self):
        """create(): Creating multiple cells should return a list of GIDs"""
        ifcell = nest.create(nest.IF_curr_alpha,n=10)
        assert ifcell == range(1,11), 'Failed to create 10 standard cells'
       
    def testCreateStandardCellsWithNegative_n(self):
        """create(): n must be positive definite"""
        self.assertRaises(AssertionError, nest.create, nest.IF_curr_alpha, n=-1)
       
    def testCreateStandardCellWithParams(self):
        """create(): Parameters set on creation should be the same as retrieved with getDict()"""
        ifcell = nest.create(nest.IF_curr_alpha,{'tau_syn':3.141592654})
        ifcell_params = nest.pynest.getDict([ifcell])
        assert ifcell_params[0]['TauSyn'] == 3.141592654
 
    def testCreateNESTCell(self):
        """create(): First cell created should have GID==1"""
        ifcell = nest.create('iaf_neuron')
        assert ifcell == 1, 'Failed to create NEST-specific cell'
    
    def testCreateNonExistentCell(self):
        """create(): Trying to create a cell type which is not a standard cell or
        a NEST cell should raise a SLIError."""
        self.assertRaises(nest.pynest.SLIError, nest.create, 'qwerty')
    
    #def testCreateWithInvalidParameter(self):
    #    """create(): Creating a cell with an invalid parameter should raise an Exception."""
    #    self.assertRaises(common.InvalidParameterError, nest.create, 'IF_curr_alpha', {'tau_foo':3.141592654})        
    
    #def __del__(self):
    #    nest.end()


# ==============================================================================
class ConnectionTest(unittest.TestCase):
    """Tests of the connect() function."""
    
    def setUp(self):
        nest.setup(timestep=0.1,max_delay=5.0)
        self.postcells = nest.create(nest.IF_curr_alpha,n=3)
        self.precells = nest.create(nest.SpikeSourcePoisson,n=5)
        
    def testConnectTwoCells(self):
        """connect(): The first connection created should have id 0."""
        conn = nest.connect(self.precells[0],self.postcells[0])
        assert conn == 0, 'Error creating connection'
        
    def testConnectTwoCellsWithWeight(self):
        """connect(): Weight set should match weight retrieved."""
        conn_id = nest.connect(self.precells[0],self.postcells[0],weight=0.1234)
        weight = nest.pynest.getWeight(nest.pynest.getAddress(self.precells[0]),conn_id)
        assert weight == 0.1234*1000, "Weight set does not match weight retrieved." # note that pyNN.nest uses nA for weights, whereas NEST uses pA

    def testConnectTwoCellsWithDelay(self):
        """connect(): Delay set should match delay retrieved."""
        conn_id = nest.connect(self.precells[0],self.postcells[0],delay=4.321)
        delay = nest.pynest.getDelay(nest.pynest.getAddress(self.precells[0]),conn_id)
        assert delay == 4.3, "Delay set does not match delay retrieved." # Note that delays are only stored to the precision of the timestep.

    def testConnectManyToOne(self):
        """connect(): Connecting n sources to one target should return a list of size n, each element being the target port."""
        connlist = nest.connect(self.precells,self.postcells[0])
        assert connlist == [0]*len(self.precells)
        
    def testConnectOneToMany(self):
        """connect(): Connecting one source to n targets should return a list of target ports."""
        connlist = nest.connect(self.precells[0],self.postcells)
        assert connlist == [0,1,2]
        
    def testConnectManyToMany(self):
        """connect(): Connecting m sources to n targets should return a list of length m x n"""
        connlist = nest.connect(self.precells,self.postcells)
        assert connlist == [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]
        
    def testConnectWithProbability(self):
        """connect(): If p=0.5, it is very unlikely that either zero or the maximum number of connections should be created."""
        connlist = nest.connect(self.precells,self.postcells,p=0.5)
        assert 0 < len(connlist) < len(self.precells)*len(self.postcells), 'Number of connections is %d: this is very unlikely (although possible).' % len(connlist)
    
    def testConnectNonExistentPreCell(self):
        """connect(): Connecting from non-existent cell should raise a ConnectionError."""
        self.assertRaises(common.ConnectionError, nest.connect, 12345, self.postcells[0])
        
    def testConnectNonExistentPostCell(self):
        """connect(): Connecting to a non-existent cell should raise a ConnectionError."""
        self.assertRaises(common.ConnectionError, nest.connect, self.precells[0], 45678)
        
    def testDelayTooSmall(self):
        """connect(): Setting a delay smaller than min_delay should raise an Exception.""" 
        self.assertRaises(common.ConnectionError, nest.connect, self.precells[0], self.postcells[0], delay=0.0)
           
    def testDelayTooLarge(self):
        """connect(): Setting a delay larger than max_delay should raise an Exception.""" 
        self.assertRaises(common.ConnectionError, nest.connect, self.precells[0], self.postcells[0], delay=1000.0)

    #def __del__(self):
    #    nest.end()

# ==============================================================================        
class SetValueTest(unittest.TestCase): pass # to write later

# ==============================================================================
class RecordSpikesTest(unittest.TestCase): pass # to write later

# ==============================================================================
class RecordVTest(unittest.TestCase): pass # to write later

# ==============================================================================    
class PopulationInitTest(unittest.TestCase):
    """Tests of the __init__() method of the Population class."""
    
    def setUp(self):
        nest.setup()
        nest.Population.nPop = 0
        
    def testSimpleInit(self):
        """Population.__init__(): should return a numpy array and give a default label."""
        net = nest.Population((3,3), nest.IF_curr_alpha)
        # shouldn't really have two assertions in one test but I'm lazy
        assert net.label == 'population0'                  
        assert numpy.equal(net.cell, numpy.array([[1,2,3],[4,5,6],[7,8,9]])).all() 
        
    def testInitWithParams(self):
        """Population.__init__(): Parameters set on creation should be the same as retrieved with getDict()"""
        net = nest.Population((3,3),nest.IF_curr_alpha,{'tau_syn':3.141592654})
        ifcell_params = nest.pynest.getDict([net.cell[0,0]])
        assert ifcell_params[0]['TauSyn'] == 3.141592654
    
    def testInitWithLabel(self):
        """Population.__init__(): A label set on initialisation should be retrievable with the Population.label attribute."""
        net = nest.Population((3,3),nest.IF_curr_alpha,label='iurghiushrg')
        assert net.label == 'iurghiushrg'
    
#    def testInvalidCellType(self):
#        """Population.__init__(): Trying to create a cell type which is not a method of StandardCells #should raise an AttributeError."""
#        self.assertRaises(AttributeError, nest.Population, (3,3), 'qwerty')
    
    #def __del__(self):
    #    nest.end()
    
    def testInitWithNonStandardModel(self):
        """Population.__init__(): should return a numpy array and give a default label."""
        net = nest.Population((3,3), 'iaf_neuron')
        assert net.label == 'population0'                  
        assert numpy.equal(net.cell, numpy.array([[1,2,3],[4,5,6],[7,8,9]])).all() 

# ==============================================================================
class PopulationIndexTest(unittest.TestCase):
    """Tests of the Population class indexing."""
    
    def setUp(self):
        nest.setup()
        nest.Population.nPop = 0
        self.net = nest.Population((10,),nest.IF_curr_alpha)
    
    def testValidIndices(self):
        for i in range(10):
            self.assertEqual((i,),self.net.locate(self.net[i]))

    def testInvalidIndices(self):
        self.assertRaises(IndexError, self.net.__getitem__, (11,))
        
    def testInvalidIndexDimension(self):
        self.assertRaises(common.InvalidDimensionsError, self.net.__getitem__, (10,2))

# ==============================================================================
class PopulationSetTest(unittest.TestCase):
    """Tests of the set(), tset() and rset() methods of the Population class."""

    #def __del__(self):
    #    nest.end()
        
    def setUp(self):
        nest.setup()
        nest.Population.nPop = 0
        self.net = nest.Population((3,3),nest.IF_curr_alpha)
        self.net2 = nest.Population((5,),'iaf_neuron')
    
    def testSetFromDict(self):
        """Parameters set in a dict should all be retrievable using pynest.getDict()"""
        self.net.set({'tau_m':43.21})
        assert nest.pynest.getDict([self.net.cell[0,0]])[0]['Tau'] == 43.21
    
    def testSetFromPair(self):
        """A parameter set as a string,value pair should be retrievable using pynest.getDict()"""
        self.net.set('tau_m',12.34)
        assert nest.pynest.getDict([self.net.cell[0,0]])[0]['Tau'] == 12.34
    
    def testSetInvalidFromPair(self):
        """Trying to set an invalid value for a parameter should raise an exception."""
        self.assertRaises(common.InvalidParameterValueError, self.net.set, 'tau_m', [])
    
    def testSetInvalidFromDict(self):
        """When any of the parameters in a dict have invalid values, then an exception should be raised.
           There is no guarantee that the valid parameters will be set."""
        self.assertRaises(common.InvalidParameterValueError, self.net.set, {'v_thresh':'hello','tau_m':56.78})
    
    def testSetNonexistentFromPair(self):
        """Trying to set a nonexistent parameter should raise an exception."""
        self.assertRaises(common.NonExistentParameterError, self.net.set, 'tau_foo', 10.0)
    
    def testSetNonexistentFromDict(self):
        """When some of the parameters in a dict are inexistent, an exception should be raised.
           There is no guarantee that the existing parameters will be set."""
        self.assertRaises(common.NonExistentParameterError, self.net.set, {'tau_foo': 10.0, 'tau_m': 21.0})
    
    def testSetWithNonStandardModel(self):
        """Parameters set in a dict should all be retrievable using pynest.getDict()"""
        self.net2.set({'Tau':43.21})
        assert nest.pynest.getDict([self.net2.cell[0]])[0]['Tau'] == 43.21
    
    def testTSet(self):
        """The valueArray passed should be retrievable using pynest.getDict() on all nodes."""
        array_in = numpy.array([[0.1,0.2,0.3],[0.4,0.5,0.6],[0.7,0.8,0.9]])
        self.net.tset('i_offset', array_in)
        tmp = nest.pynest.getDict(list(self.net.cell.reshape((9,))))
        tmp = [d['I0'] for d in tmp]
        array_out = numpy.array(tmp).reshape((3,3))
        assert numpy.equal(array_in, array_out).all()
    
    def testTSetInvalidDimensions(self):
        """If the size of the valueArray does not match that of the Population, should raise an InvalidDimensionsError."""
        array_in = numpy.array([[0.1,0.2,0.3],[0.4,0.5,0.6]])
        self.assertRaises(common.InvalidDimensionsError, self.net.tset, 'i_offset', array_in)
    
    def testTSetInvalidValues(self):
        """If some of the values in the valueArray are invalid, should raise an exception."""
        array_in = numpy.array([[0.1,0.2,0.3],[0.4,0.5,0.6],[0.7,0.8,'apples']])
        self.assertRaises(common.InvalidParameterValueError, self.net.tset, 'i_offset', array_in)
        
    def testRSetNumpy(self):
        """Population.rset(): with numpy rng."""
        rd1 = random.RandomDistribution(rng=random.NumpyRNG(seed=98765),
                                         distribution='uniform',
                                         parameters=[0.9,1.1])
        rd2 = random.RandomDistribution(rng=random.NumpyRNG(seed=98765),
                                         distribution='uniform',
                                         parameters=[0.9,1.1])
        self.net.rset('cm',rd1)
        tmp = nest.pynest.getDict(list(self.net.cell.reshape((9,))))
        output_values = [d['C'] for d in tmp]
        input_values = rd2.next(9)
        for i in range(9):
            self.assertAlmostEqual(input_values[i],output_values[i],places=5)
            
# ==============================================================================
class PopulationCallTest(unittest.TestCase): # to write later
    """Tests of the call() and tcall() methods of the Population class."""
    pass

# ==============================================================================
class PopulationRecordTest(unittest.TestCase): # to write later
    """Tests of the record(), record_v(), printSpikes(), print_v() and
       meanSpikeCount() methods of the Population class."""
    def setUp(self):
	nest.setup()
        nest.Population.nPop = 0
	self.pop1 = nest.Population((3,3), nest.SpikeSourcePoisson,{'rate': 20})
	self.pop2 = nest.Population((3,3), nest.IF_curr_alpha)

    def testRecordAll(self):
        """Population.record(): not a full test, just checking there are no Exceptions raised."""
	self.pop1.record()
        
    def testRecordInt(self):
        """Population.record(n): not a full test, just checking there are no Exceptions raised."""
        # Partial record	
	self.pop1.record(5)
	
    def testRecordWithRNG(self):
        """Population.record(n,rng): not a full test, just checking there are no Exceptions raised."""
	self.pop1.record(5,random.NumpyRNG())
        
    def testRecordList(self):
        """Population.record(list): not a full test, just checking there are no Exceptions raised."""
	# Selected list record
	record_list = []
	for i in range(0,2):
	    record_list.append(self.pop1[i,1])
	self.pop1.record(record_list)	
   
    def testSpikeRecording(self):
	# We test the mean spike count by checking if the rate of the poissonian sources are
	# close to 20 Hz. Then we also test how the spikes are saved
	self.pop1.record()
	simtime = 1000
	nest.run(simtime)
	self.pop1.printSpikes("temp_nest.ras")
	rate = self.pop1.meanSpikeCount()*1000/simtime
	assert (20*0.8 < rate) and (rate < 20*1.2)
	
    def testPotentialRecording(self):
	"""Population.record_v() and Population.print_v(): not a full test, just checking 
	# there are no Exceptions raised."""
	rng = random.NumpyRNG(123)
	v_reset  = -65.0
	v_thresh = -50.0
	uniformDistr = random.RandomDistribution(rng,'uniform',[v_reset,v_thresh])
	self.pop2.randomInit(uniformDistr)
	self.pop2.record_v([self.pop2[0,0], self.pop2[1,1]])
	simtime = 10
        nest.run(simtime)
	self.pop2.print_v("temp_nest.v")

# ==============================================================================
class ProjectionInitTest(unittest.TestCase):
    """Tests of the __init__() method of the Projection class."""
        
    def setUp(self):
        nest.setup(max_delay=0.5)
        nest.Population.nPop = 0
        self.target33 = nest.Population((3,3),nest.IF_curr_alpha)
        self.target6  = nest.Population((6,),nest.IF_curr_alpha)
        self.source5  = nest.Population((5,),nest.SpikeSourcePoisson)
        self.source22 = nest.Population((2,2),nest.SpikeSourcePoisson)
        self.source33 = nest.Population((3,3),nest.SpikeSourcePoisson)

    def testAllToAll(self):
        """For all connections created with "allToAll" it should be possible to obtain the weight using pynest.getWeight()"""
        for srcP in [self.source5, self.source22]:
            for tgtP in [self.target6, self.target33]:
                prj1 = nest.Projection(srcP, tgtP, "allToAll")
                assert len(prj1._sources) == len(prj1._targets)
                weights = []
                for src,tgt in prj1.connections():
                    weights.append(nest.pynest.getWeight(src,tgt))
                assert weights == [1.0]*len(prj1._sources)
    
    def testdistantDependentProbability(self):
        """For all connections created with "distanceDependentProbability" it should be possible to obtain the weight using pyneuron.getWeight()"""
        # Test should be improved..."
        distrib_Numpy = random.RandomDistribution(random.NumpyRNG(12345),'uniform',(0,1)) 
        prj1 = nest.Projection(self.source33, self.target33, 'distanceDependentProbability',{'d_expression' : 'exp(-d)'}, distrib_Numpy)
        prj2 = nest.Projection(self.source33, self.target33, 'distanceDependentProbability',{'d_expression' : 'd < 0.5'}, distrib_Numpy)
        assert (0 < len(prj1) < len(self.source33)*len(self.target33)) and (0 < len(prj2) < len(self.source33)*len(self.target33))
        
    def testFixedProbability(self):
        """For all connections created with "fixedProbability" it should be possible to obtain the weight using pynest.getWeight()"""
        for srcP in [self.source5, self.source22]:
            for tgtP in [self.target6, self.target33]:
                prj1 = nest.Projection(srcP, tgtP, "fixedProbability", 0.5)
                assert len(prj1._sources) == len(prj1._targets)
                weights = []
                for src, tgt in prj1.connections():
                    weights.append(nest.pynest.getWeight(src,tgt))
                assert weights == [1.0]*len(prj1._sources)
                
    def testSaveAndLoad(self):
        prj1 = nest.Projection(self.source22, self.target33, 'allToAll')
        prj1.setDelays(0.2)
        prj1.setWeights(1.234)
        prj1.saveConnections("connections.tmp")
        prj2 = nest.Projection(self.source22, self.target33, 'fromFile',"connections.tmp")
        w1 = []; w2 = []; d1 = []; d2 = [];
        # For a connections scheme saved and reloaded, we test if the connections, their weights and their delays
        # are equal.
        for src,tgt in prj1.connections():
            w1.append(nest.pynest.getWeight(src,tgt))
            d1.append(nest.pynest.getDelay(src,tgt))
        for src,tgt in prj2.connections():
            w2.append(nest.pynest.getWeight(src,tgt))
            d2.append(nest.pynest.getDelay(src,tgt))
        assert (w1 == w2) and (d1 == d2)

class ProjectionSetTest(unittest.TestCase):
    """Tests of the setWeights(), setDelays(), setThreshold(),
       randomizeWeights() and randomizeDelays() methods of the Projection class."""

    def setUp(self):
        nest.setup(max_delay=0.5)
        nest.Population.nPop = 0
        self.target33 = nest.Population((3,3),nest.IF_curr_alpha)
        self.target6  = nest.Population((6,),nest.IF_curr_alpha)
        self.source5  = nest.Population((5,),nest.SpikeSourcePoisson)
        self.source22 = nest.Population((2,2),nest.SpikeSourcePoisson)
        self.prjlist = []
        self.distrib_Numpy = random.RandomDistribution(random.NumpyRNG(12345),'uniform',(0.1,0.5)) 
        for tgtP in [self.target6, self.target33]:
            for srcP in [self.source5, self.source22]:
                for method in ('allToAll', 'fixedProbability'):
                    self.prjlist.append( nest.Projection(srcP,tgtP,method,{'p_connect':0.5}) )

    def testSetWeightsToSingleValue(self):
        """Weights set using setWeights() should be retrievable with pynest.getWeight()"""
        for prj in self.prjlist:
            prj.setWeights(1.234)
            for src, tgt in prj.connections():
                assert nest.pynest.getWeight(src,tgt) == 1234.0 # note the difference in units between pyNN and NEST

    #def testSetAndGetID(self):
        # Small test to see if the ID class is working
        #self.target33[0,2].set({'tau_m' : 15.1})
        #assert (self.target33[0,2].get('tau_m') == 15.1)
        
    def testSetAndGetPositionID(self):
        # Small test to see if the position of the ID class is working
        self.target33[0,2].setPosition((0.5,1.5))
        assert (self.target33[0,2].getPosition() == (0.5,1.5))
        
    def testrandomizeWeights(self):
        # The probability of having two consecutive weights vector that are equal should be 0
        prj1 = nest.Projection(self.source5, self.target33, 'allToAll')
        prj1.randomizeWeights(self.distrib_Numpy)
        w1 = []; w2 = [];
        for src,tgt in prj1.connections():
            w1.append(nest.pynest.getWeight(src,tgt))
        prj1.randomizeWeights(self.distrib_Numpy)        
        for src, tgt in prj1.connections():
            w2.append(nest.pynest.getWeight(src,tgt)) 
        self.assertNotEqual(w1,w2)
        
    def testrandomizeDelays(self):
        # The probability of having two consecutive weights vector that are equal should be 0
        prj1 = nest.Projection(self.source5, self.target33, 'allToAll')
        prj1.randomizeDelays(self.distrib_Numpy)
        d1 = []; d2 = [];
        for src,tgt in prj1.connections():
            d1.append(nest.pynest.getDelay(src,tgt))
        prj1.randomizeDelays(self.distrib_Numpy)        
        for src, tgt in prj1.connections():
            d2.append(nest.pynest.getDelay(src,tgt)) 
        self.assertNotEqual(d1,d2)

if __name__ == "__main__":
    unittest.main()
    