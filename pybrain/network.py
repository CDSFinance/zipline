
import numpy
from pybrain.structure import FeedForwardNetwork
from pybrain.structure import RecurrentNetwork
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection
from pybrain.structure import IdentityConnection

from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer

# Build the neural network
net = RecurrentNetwork()

# Add nodes to the recurrent neural network
net.addInputModule(LinearLayer(7, name="in"))
#net.addModule(SigmoidLayer(3, name="hidden"))
net.addOutputModule(LinearLayer(1, name="out"))

net.addConnection(FullConnection(net['in'], net['out'], name='in_out'))
net.addRecurrentConnection(IdentityConnection(net['out'], net['in'], name='r1', outSliceFrom=0, outSliceTo=1))
net.addRecurrentConnection(IdentityConnection(net['out'], net['in'], name='r2', outSliceFrom=1, outSliceTo=2))
net.addRecurrentConnection(IdentityConnection(net['out'], net['in'], name='r3', outSliceFrom=2, outSliceTo=3))
net.addRecurrentConnection(IdentityConnection(net['out'], net['in'], name='r4', outSliceFrom=3, outSliceTo=4))
net.sortModules()

# data = SupervisedDataSet(2, 1)
# data.addSample((0,0), (0,))
# data.addSample((1,0), (1,))
# data.addSample((0,1), (1,))
# data.addSample((1,1), (0,))

# trainer = BackpropTrainer(net, data)
# trainer.trainUntilConvergence()

print net
print net.params

# print net.activate([1,1])
# print net.activate([1,1])
# print net.activate([1,1])
# print net.activate([1,1])
# net.reset()
# print net.activate([1,1])
# print net.activate([1,1])
# print net.activate([1,1])
# print net.activate([1,1])














