import socket
import traci
import pickle
import numpy as np
from math import inf, nan
import pandas as pd

projectPath = 'C:\\Users\H2_ha\\2024-05-14-12-53-58\\osm.sumocfg'
personalCapacity = {
    'bike_bicycle': 1,
    'motorcycle_motorcycle': 2,
    'veh_passenger': 4,
    'truck_truck': 3,
    'bus_bus': 85
}

maxSpeed = {
            'bike_bicycle': 50,
            'motorcycle_motorcycle': 200,
            'veh_passenger': 200,
            'truck_truck': 130,
            'bus_bus': 85
        }

vehicleOneHotEncoder = pickle.load(open('vehicleOneHotEncoder', 'rb'))
myModel = pickle.load(open('RandomForestRegressor', 'rb'))

host = socket.gethostname()
port = 2000
data = None
server_socket = socket.socket()  # get instance
server_socket.bind((host, port))  # bind host address and port together

# configure how many client the server can listen simultaneously
server_socket.listen(1)
print('Waiting for connection...')
conn, address = server_socket.accept()  # accept new connection
print("Connection from: " + str(address))

while True:
    # receive data stream. it won't accept data packet greater than 1024 bytes
    data = eval(conn.recv(1024).decode())
    if data:
        conn.close()  # close the connection
        break

def nextTrafficLight(tls:list):
    minDistance = float(inf)
    closestTL = None
    for tl in tls:
        if tl:
            if tl[2]< minDistance:
                minDistance = tl[2]
                closestTL = tl
    return closestTL

# def accel(v_type):
#     try:
#         return traci.vehicle.getAccel(v_type)
#     except:
#         data = {
#             'bike_bicycle': 1.2,
#             'motorcycle_motorcycle': 6,
#             'veh_passenger': 2.6,
#             'truck_truck': 1.3,
#             'bus_bus': 1.2
#         }
#         return data[v_type]

def width(v_type):
    try:
        return traci.vehicle.getWidth(v_type)
    except:
        data = {
            'bike_bicycle': 0.65,
            'motorcycle_motorcycle': 0.9,
            'veh_passenger': 1.8,
            'truck_truck': 2.4,
            'bus_bus': 2.5
        }
        return data[v_type]
    
def height(v_type):
    try:
        return traci.vehicle.getHeight(v_type)
    except:
        data = {
            'bike_bicycle': 1.7,
            'motorcycle_motorcycle': 1.5,
            'veh_passenger': 1.5,
            'truck_truck': 2.4,
            'bus_bus': 3.4
        }
        return data[v_type]

try:
    point_debut = data['point_debut']
    point_fin = data['point_fin']
    autonomousVehicleID = data['autonomousVehicleID']
    vehicleType = data['vehicleType']
    traci.start(["sumo-gui", "-c", projectPath])
    traci.route.add('userRoute'+point_debut+'@'+point_fin, [point_debut, point_fin])
except:
    pass
personIn = np.random.randint(1, personalCapacity[vehicleType] + 1)
traci.vehicle.add(vehID=autonomousVehicleID, routeID='userRoute'+point_debut+'@'+point_fin, typeID=vehicleType, personCapacity=personalCapacity[vehicleType], personNumber=personIn, departSpeed='5')

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()
    if autonomousVehicleID in vehicles:
        x, y = traci.vehicle.getPosition(autonomousVehicleID)
        edgeID = traci.vehicle.getRoadID(autonomousVehicleID)
        nextTLS = traci.vehicle.getNextTLS(autonomousVehicleID)
        closestTL = nextTrafficLight(nextTLS)
        laneID = traci.vehicle.getLaneID(autonomousVehicleID)
        dataTOencode = {
            'vehicleChangeLaneToLeft': [traci.vehicle.couldChangeLane(autonomousVehicleID, 1)],
            'vehicleChangeLaneToRight': [traci.vehicle.couldChangeLane(autonomousVehicleID, -1)],
            'vehicleType': [vehicleType],
            'closestTfState': [closestTL[3] if closestTL else str(nan)]
        }
        encoded_data = vehicleOneHotEncoder.transform(pd.DataFrame(dataTOencode))
        encoded_df = pd.DataFrame(encoded_data, columns=vehicleOneHotEncoder.get_feature_names_out(['vehicleChangeLaneToLeft', 'vehicleChangeLaneToRight', 'vehicleType', 'closestTfState']))

        vehicleData = {
            'xPosition': x,
            'yPosition': y,
            'vehicleMaxSpeed': maxSpeed[vehicleType],
            'closestTfDistance': closestTL[2] if closestTL else nan,
            'vehicleAcceleration': traci.vehicle.getAcceleration(autonomousVehicleID),
            # 'vehicleMaxAcceleration': accel(vehicleType),
            'vehicleAngle': traci.vehicle.getAngle(autonomousVehicleID),
            'vehicleDisplacement': traci.vehicle.getDistance(autonomousVehicleID),
            # 'vehicleAllowedSpeed': traci.vehicle.getAllowedSpeed(autonomousVehicleID),
            'edgeLaneNumber': traci.edge.getLaneNumber(edgeID),
            'LaneMaxSpeed': traci.lane.getMaxSpeed(laneID),
            'vehicleSignals': traci.vehicle.getSignals(autonomousVehicleID),
            'vehicleFuelConsumption': traci.vehicle.getFuelConsumption(autonomousVehicleID),
            'vehicleWidth': width(vehicleType),
            # 'vehicleHeight': height(vehicleType),
            'vehicleChangeLaneToLeft_True': encoded_df['vehicleChangeLaneToLeft_True'],
            'vehicleChangeLaneToRight_True': encoded_df['vehicleChangeLaneToRight_True'],
            'vehicleType_bike_bicycle': encoded_df['vehicleType_bike_bicycle'],
            'vehicleType_bus_bus': encoded_df['vehicleType_bus_bus'],
            'vehicleType_motorcycle_motorcycle': encoded_df['vehicleType_motorcycle_motorcycle'],
            'vehicleType_truck_truck': encoded_df['vehicleType_truck_truck'],
            'vehicleType_veh_passenger': encoded_df['vehicleType_veh_passenger'],
            'closestTfState_G': encoded_df['closestTfState_G'],
            'closestTfState_g': encoded_df['closestTfState_g'],
            'closestTfState_nan': encoded_df['closestTfState_nan'],
            'closestTfState_r': encoded_df['closestTfState_r'],
            'closestTfState_y': encoded_df['closestTfState_y']
        }
        generatedSpeed = myModel.predict(pd.DataFrame(vehicleData))
        traci.vehicle.setSpeed(autonomousVehicleID, generatedSpeed)