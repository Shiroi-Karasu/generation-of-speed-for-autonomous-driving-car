import traci
import math
import pandas as pd

# import firebase_admin
# from firebase_admin import credentials
# from dotenv import load_dotenv
# import os
# from firebase_admin import firestore

# load_dotenv('../auth.env')
# cred = credentials.Certificate(os.getenv('pathToServiceAccountKey'))
# firebase_admin.initialize_app(cred)
# DataBase = firestore.client()

projectPath = 'C:\\Users\H2_ha\\2024-05-14-12-53-58\\osm.sumocfg'
traci.start(["sumo", "-c", projectPath])

def maxSpeed(v_type):
    try:
        return traci.vehicle.getMaxSpeed(v_type)
    except:
        data = {
            'bike_bicycle': 50,
            'motorcycle_motorcycle': 200,
            'veh_passenger': 200,
            'truck_truck': 130,
            'bus_bus': 85
        }  
        return data[v_type]
 
def accel(v_type):
    try:
        return traci.vehicle.getAccel(v_type)
    except:
        data = {
            'bike_bicycle': 1.2,
            'motorcycle_motorcycle': 6,
            'veh_passenger': 2.6,
            'truck_truck': 1.3,
            'bus_bus': 1.2
        }
        return data[v_type]
    
def decel(v_type):
    try:
        return traci.vehicle.getDecel(v_type)
    except:
        data = {
            'bike_bicycle': 3,
            'motorcycle_motorcycle': 10,
            'veh_passenger': 4.5,
            'truck_truck': 4,
            'bus_bus': 4
        }
        return data[v_type]
       
def length(v_type):
    try:
        return traci.vehicle.getLength(v_type)
    except:
        data = {
            'bike_bicycle': 1.6,
            'motorcycle_motorcycle': 2.2,
            'veh_passenger': 5,
            'truck_truck': 7.1,
            'bus_bus': 12
        }
        return data[v_type]
    
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
    
def personCapacity(v_type):
    try:
        return traci.vehicle.getPersonCapacity(v_type)
    except:
        data = {
            'bike_bicycle': 1,
            'motorcycle_motorcycle': 2,
            'veh_passenger': 4,
            'truck_truck': 3,
            'bus_bus': 85
        }
        return data[v_type]

i = 1
VehiclesData = []

while traci.simulation.getMinExpectedNumber() > 0 and i < 20001:
    traci.simulationStep()
    vehiclesIDs = traci.vehicle.getIDList()
    for vehicleID in vehiclesIDs:
        if i < 20001:
            x, y = traci.vehicle.getPosition(vehicleID)
            edgeID = traci.vehicle.getRoadID(vehicleID)
            vType = traci.vehicle.getTypeID(vehicleID)
            laneID = traci.vehicle.getLaneID(vehicleID)
            # minDistance = round(traci.lane.getLength(laneID) - traci.vehicle.getLanePosition(vehicleID)) + 1

            vehicleData = {
                'vehicleID': vehicleID,
                'vehicleType': vType,
                'vehicleSpeed': traci.vehicle.getSpeed(vehicleID),
                'vehicleMaxSpeed': maxSpeed(vType),
                'vehicleLateralSpeed': traci.vehicle.getLateralSpeed(vehicleID),
                'vehicleAcceleration': traci.vehicle.getAcceleration(vehicleID),
                'vehicleMaxAcceleration': accel(vType),
                'vehicleMaxDeceleration': decel(vType),
                'vehiclePosition(x,y)': list(traci.vehicle.getPosition(vehicleID)),
                'vehicleGPSposition[longitude, latitude]': list(traci.simulation.convertGeo(x, y)),
                'vehicleAngle': traci.vehicle.getAngle(vehicleID),
                'vehicleDisplacement': traci.vehicle.getDistance(vehicleID),
                'vehicleAllowedSpeed': traci.vehicle.getAllowedSpeed(vehicleID),
                'edgeID': edgeID,
                'edgeLaneNumber': traci.edge.getLaneNumber(edgeID),
                'laneID': laneID,
                'LaneMaxSpeed': traci.lane.getMaxSpeed(laneID),
                'vehicleSignals': traci.vehicle.getSignals(vehicleID),
                'vehicleElectricityConsumption': traci.vehicle.getElectricityConsumption(vehicleID),
                'vehicleFuelConsumption': traci.vehicle.getFuelConsumption(vehicleID),
                'vehicleStopState': traci.vehicle.getStopState(vehicleID),
                'vehicleLenght': length(vType),
                'vehicleWidth': width(vType),
                'vehicleHeight': height(vType),
                'vehiclePersonCapacity': personCapacity(vType),
                'vehicleChangeLaneToRight': traci.vehicle.couldChangeLane(vehicleID, -1),
                'vehicleChangeLaneToLeft': traci.vehicle.couldChangeLane(vehicleID, 1),
                'nextTLS': []
            }

            nextTLS = traci.vehicle.getNextTLS(vehicleID)
            for tls_info in nextTLS:
                vehicleData['nextTLS'].append({
                    'tlsID': tls_info[0],
                    'tlsIndex': tls_info[1],
                    'distance': tls_info[2],
                    'state': tls_info[3]
                })

            # currentDocument = DataBase.collection('Vehicles_16_07').document() 
            # currentDocument.set(vehicleData)
            VehiclesData.append(vehicleData)
            i += 1
        else:
            break

traci.close()
VehiclesDataframe = pd.DataFrame(VehiclesData)
VehiclesDataframe.to_csv('vehiclesData.csv')