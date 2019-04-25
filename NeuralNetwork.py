import sys
import numpy as np
import random
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization

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
ETData = load("ETData.txt")

# Format NDVI Data
for i in range(len(ndviData)):
    if(ndviData[i] != "List (23 elements)" and ndviData[i] != "N"):
        # Convert string into int
        ndviData[i] = int(ndviData[i])/1000
    elif(ndviData[i] == "N"):
        # If the current value equals 'N', convert it into type None
        ndviData[i] = None
# Convert NDVI data into Numpy array and split it into multidimensional array
ndviArr = np.array(ndviData)
ndviOut = np.split(ndviArr, 400)

# Remove first element in each array
ndviFormatted = [ndviOut[i][1:] for i in range(400)]

# Format ET Data
for i in range(len(ETData)):
    if(ETData[i] != "List (23 elements)" and ETData[i] != "[]" and ETData[i] != "N"):
        # Convert string into int
        ETData[i] = int(ETData[i])/500
    elif(ETData[i] == "[]" or ETData[i] == "N"):
        # If the current value equals '[]', convert it into type None
        ETData[i] = None
# Convert ET data into Numpy array and split it into multidimensional array
ETArr = np.array(ETData)
ETOut = np.split(ETArr, 400)

# Remove first element in each array
ETFormatted = [ETOut[i][1:] for i in range(400)]

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

# Combine data into multidimensional array, with each element being in the format of [temperature, NDVI, ET] for a given point on a given day.
temperatureData = np.zeros(shape=(141200, 3))
temperatureDataCount = 0
for i in range(len(tempFormatted)):
    for n in range(len(tempFormatted[i])):
        if(n == 352):
            break
        else:
            if(n > 15):
                if((n + 1) % 16 == 0):
                    ndviValue = int((n+1)/16) - 1
                    ETValue = int((n+1)/16) - 1
                    temperatureData[temperatureDataCount] = [tempFormatted[i][n], ndviFormatted[i][ndviValue], ETFormatted[i][ETValue]]
                else:
                    ndviValue = int(((n+1)-((n+1)%16))/16) - 1
                    ETValue = int(((n+1)-((n+1)%16))/16) - 1
                    temperatureData[temperatureDataCount] = [tempFormatted[i][n], ndviFormatted[i][ndviValue], ETFormatted[i][ETValue]]
            else:
                temperatureData[temperatureDataCount] = [tempFormatted[i][n], ndviFormatted[i][0], ETFormatted[i][0]]
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

chosenFireData = np.zeros(shape=((4780 * 2), 1))
chosenData = np.zeros(shape=((4780 * 2), 3))

fireCount = 0
nonFireCount = 0
for i in range(len(fireData)):
    if(fireData[i] == 1 and not np.isnan(temperatureData[i][0]) and not np.isnan(temperatureData[i][1]) and not np.isnan(temperatureData[i][2]) and not np.isnan(fireData[i]) and fireCount <= 4780):
        chosenFireData[fireCount] = fireData[i]
        chosenData[fireCount] = temperatureData[i]
        fireCount += 1

indexCount = 4780
for n in range(4780):
    while True:
        index = random.randint(0, len(fireData) - 1)
        if(fireData[index] == 0 and not np.isnan(fireData[index]) and not np.isnan(temperatureData[index][0]) and not np.isnan(temperatureData[index][1]) and not np.isnan(temperatureData[index][2]) and nonFireCount <= 4780):
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
    if(chosenData[i][0] != 0 and chosenData[i][1] != 0 and chosenData[i][2] != 0):
        filteredFireData.append(chosenFireData[i])
        filteredData.append(chosenData[i].tolist())


filteredFireData = np.array(filteredFireData)
filteredData = np.array(filteredData)

testingFireData = filteredFireData
testingData = filteredData

print(len(filteredData))

filteredFireData = filteredFireData[1:9525]
filteredData = filteredData[1:9525]

fireCount = 0
nonFireCount = 0
for i in range(len(filteredFireData)):
    if(filteredFireData[i] == 1):
        fireCount += 1
    elif(filteredFireData[i] == 0):
        nonFireCount += 1

print(filteredData[0])
print(filteredFireData[0])
model = Sequential()

model.add(Dense(128, input_shape=(3,)))
model.add(BatchNormalization())
model.add(Activation("elu"))

model.add(Dense(128))
model.add(BatchNormalization())
model.add(Activation("elu"))

model.add(Dense(128))
model.add(BatchNormalization())
model.add(Activation("elu"))

model.add(Dense(1))
model.add(BatchNormalization())
model.add(Activation("sigmoid"))

model.compile(loss="mean_squared_error", optimizer="adam", metrics=["accuracy"])

model.fit(filteredData, filteredFireData, batch_size=32, epochs=20, validation_split=0.15, shuffle=True)

predictions = model.predict(testingData[0].reshape((1,3)))
print(predictions[0][0])
print(testingFireData[0])

filename = "chosenData.txt"
newFile = open(filename, 'w')

for line in range(len(filteredData)):
    newFile.write(str(filteredData[line]) + ' - ' + str(filteredFireData[line]) + '\n')

newFile.close()
