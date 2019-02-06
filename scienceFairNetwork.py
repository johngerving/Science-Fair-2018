import sys
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization

def load(file):
    try:
        with open(file) as in_file:
            loaded_txt = in_file.read().strip().split('\n')
            return loaded_txt
    except IOError as e:
        print("{}\nError opening {}. Terminating program.".format(e, file), file=sys.stderr)
    sys.exit(1)

# Open temperature, NDVI, and fire data files
tempData = load("TemperatureData.txt")
ndviData = load("NDVIData.txt")
fireData = load("FireData.txt")

# Format NDVI Data
for i in range(len(ndviData)):
    if(ndviData[i] != "List (23 elements)" and ndviData[i] != "N"):
        # Convert string into int
        ndviData[i] = int(ndviData[i])/10000
    elif(ndviData[i] == "N"):
        # If the current value equals 'N', convert it into type None
        ndviData[i] = None
# Convert NDVI data into Numpy array and split it into multidimensional array
ndviArr = np.array(ndviData)
ndviOut = np.split(ndviArr, 400)

# Remove first element in each array
ndviFormatted = [ndviOut[i][1:] for i in range(400)]

# Format temperature data
for i in range(len(tempData)):
    if(tempData[i] != "List (353 elements)" and tempData[i] != "N"):
        # Convert string into float
        tempData[i] = float(tempData[i])/60
    elif(tempData[i] == "N"):
        # If the current value equals 'N', convert it into type None
        tempData[i] = None
# Convert temperature data into Numpy array and split it into multidimensional array
tempArr = np.array(tempData)
tempOut = np.split(tempArr, 400)

# Remove first element in each array
tempFormatted = [tempOut[i][1:] for i in range(400)]

# Format fire data
for i in range(len(fireData)):
    if(fireData[i] != "List (353 elements)" and fireData[i] != "N"):
        # Convert string into int
        fireData[i] = int(fireData[i])
    elif(fireData[i] == "N"):
        # If the current value equals 'N', convert it into type None
        fireData[i] = None
# Convert fire data into Numpy array and split it into multidimensional array
fireArr = np.array(fireData)
fireOut = np.split(fireArr, 400)

# Remove first element in each array
fireFormatted = [fireOut[i][1:] for i in range(400)]

#Format fire data so that if there is a fire in the next 30 days, current value will be 1. Else 0.
for i in range(len(fireFormatted)):
    for n in range(len(fireFormatted[i])):
        if(len(fireFormatted[i]) - n >= 30):
            if((8 in fireFormatted[i][n:n+30] or 9 in fireFormatted[i][n:n+30]) and fireFormatted[i][n] != None):
                fireFormatted[i][n] = 1
            else:
                if(fireFormatted[i][n] != None):
                    fireFormatted[i][n] = 0
        else:
            distanceToEnd = n + ((len(fireFormatted[i]) - n) - 1)
            if((8 in fireFormatted[i][n:distanceToEnd] or 9 in fireFormatted[i][n:distanceToEnd]) and fireFormatted[i][n] != None):
                fireFormatted[i][n] = 1
            else:
                if(fireFormatted[i][n] != None):
                    fireFormatted[i][n] = 0

# Combine data into multidimensional array, with each element being in the format of [temperature, NDVI] for a given point on a given day.
temperatureData = np.zeros(shape=(141200, 2))
temperatureDataCount = 0
for i in range(len(tempFormatted)):
    for n in range(len(tempFormatted[i])):
        if(n == 352):
            break
        else:
            if(n > 15):
                if((n + 1) % 16 == 0):
                    ndviValue = int((n+1)/16) - 1
                    temperatureData[temperatureDataCount] = [tempFormatted[i][n], ndviFormatted[i][ndviValue]]
                else:
                    ndviValue = int(((n+1)-((n+1)%16))/16) - 1
                    temperatureData[temperatureDataCount] = [tempFormatted[i][n], ndviFormatted[i][ndviValue]]
            else:
                temperatureData[temperatureDataCount] = [tempFormatted[i][n], ndviFormatted[i][0]]
            temperatureDataCount += 1

# Format fire data into 1-dimensional array
fireData = np.zeros(shape=(141200, 1))
fireDataCount = 0
for i in range(len(fireFormatted)):
    for n in range(len(fireFormatted[i])):
        if(n == 352):
            break
        else:
            fireData[fireDataCount] = fireFormatted[i][n]
            fireDataCount += 1

chosenFireData = np.zeros(shape=(12200, 1))
chosenData = np.zeros(shape=(12200, 2))

fireCount = 0
nonFireCount = 0
for i in range(len(fireData)):
    if(fireData[i] == 1 and not np.isnan(temperatureData[i][0]) and not np.isnan(temperatureData[i][0]) and not np.isnan(fireData[i]) and fireCount <= 6100):
        chosenFireData[fireCount] = fireData[i]
        chosenData[fireCount] = temperatureData[i]
        fireCount += 1
indexCount = 6100
for n in range(6100):
    while True:
        index = random.randint(0, len(fireData) - 1)
        if(fireData[index] == 0 and not np.isnan(fireData[index]) and not np.isnan(temperatureData[index][0]) and not np.isnan(temperatureData[index][1]) and nonFireCount <= 6100):
            chosenFireData[indexCount] = fireData[index]
            chosenData[indexCount] = temperatureData[index]
            indexCount += 1
            nonFireCount += 1
            break
        else:
            pass

filteredFireData = []
filteredData = []

for i in range(len(chosenData)):
    if(chosenData[i][0] != 0 and chosenData[i][1] != 0):
        filteredFireData.append(chosenFireData[i])
        filteredData.append(chosenData[i].tolist())


filteredFireData = np.array(filteredFireData)
filteredData = np.array(filteredData)

testingFireData = filteredFireData
testingData = filteredData

filteredFireData = filteredFireData[1:9740]
filteredData = filteredData[1:9740]

#Create neural network - Initialize Sequential model
model = Sequential()

#Add a Dense layer with 128 neurons to the network, normalize the batch, add ELU activation function
model.add(Dense(128, input_shape=(2,)))
model.add(BatchNormalization())
model.add(Activation("elu"))

#Add a Dense layer with 128 neurons to the network, normalize the batch, add ELU activation function
model.add(Dense(128))
model.add(BatchNormalization())
model.add(Activation("elu"))

#Add a Dense layer with 128 neurons to the network, normalize the batch, add ELU activation function
model.add(Dense(128))
model.add(BatchNormalization())
model.add(Activation("elu"))

#Add output layer, with 1 neuron. Normalize the batch, then add sigmoid activation function.
model.add(Dense(1))
model.add(BatchNormalization())
model.add(Activation("sigmoid"))

#Compile the model, define loss function and optimizer
model.compile(loss="mean_squared_error", optimizer="adam", metrics=["accuracy"])

#Train the model on the training data
model.fit(filteredData, filteredFireData, batch_size=16, epochs=20, validation_split=0.15, shuffle=True)
