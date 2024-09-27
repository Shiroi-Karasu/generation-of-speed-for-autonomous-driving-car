import socket
import customtkinter
from PIL import Image
import traci
import time

edges = None
data = {'point_debut' : None,
        'point_fin' : None,
        'autonomousVehicleID' : None,
        'vehicleType' : None
        }
vehicleTypes = {
    'bicyclette': 'bike_bicycle',
    'moto': 'motorcycle_motorcycle',
    'voiture': 'veh_passenger',
    'bus': 'bus_bus',
    'Camion': 'truck_truck'
}

projectPath = 'C:\\Users\H2_ha\\2024-05-14-12-53-58\\osm.sumocfg'
try:
    traci.start(["sumo", "-c", projectPath])
    edges = traci.edge.getIDList()
    traci.close()
except:
    traci.close()

customtkinter.set_appearance_mode('dark')

app = customtkinter.CTk()
app.title('Configuration de voiture autonome')
app.grid_rowconfigure(0, weight=1)
app.resizable(width=False, height=False)

leftFrame = customtkinter.CTkFrame(app)
leftFrame.grid(row=0, column=0)
leftFrame.grid_columnconfigure((0, 1), weight=1)

optionMenu1Label = customtkinter.CTkLabel(leftFrame, text='Choisir le point de début:')
optionMenu1Label.grid(row=0, column=0, padx=10, pady=(20, 0), sticky="w", columnspan=2)
def firstPoint(choice):
    data['point_debut'] = choice

optionMenuVar1 = customtkinter.StringVar(value="Veulliez choisir un id de route")
optionMenu1 = customtkinter.CTkOptionMenu(leftFrame, values=edges, command=firstPoint, variable=optionMenuVar1)
optionMenu1.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew", columnspan=2)

optionMenu2Label = customtkinter.CTkLabel(leftFrame, text='Choisir le point final:')
optionMenu2Label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w", columnspan=2)
def lastPoint(choice):
    data['point_fin'] = choice

optionMenuVar2 = customtkinter.StringVar(value="Veulliez choisir un id de route")
optionMenu2 = customtkinter.CTkOptionMenu(leftFrame, values=edges, command=lastPoint, variable=optionMenuVar2)
optionMenu2.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew", columnspan=2)

entryLabel = customtkinter.CTkLabel(leftFrame, text='ID de véhicule:')
entryLabel.grid(row=4, column=0, padx=(10, 5), pady=(10, 0), sticky='w')
entry = customtkinter.CTkEntry(leftFrame, placeholder_text="Entrer un ID pour votre nouvelle véhicule", width=250)
entry.grid(row=5, column=0, padx=(10, 5), pady=(5, 20), sticky='ew')

typeLabel = customtkinter.CTkLabel(leftFrame, text='Type de véhicule:')
typeLabel.grid(row=4, column=1, padx=(5, 10), pady=(10, 0), sticky='w')
def typeVehicule(choice):
    data['vehicleType'] = vehicleTypes.get(choice)

optionMenuVar3 = customtkinter.StringVar(value="Quel est le type de votre véhicule?")
optionMenu3 = customtkinter.CTkOptionMenu(leftFrame, values=['bicyclette', 'moto', 'voiture', 'bus', 'Camion'], command=typeVehicule, variable=optionMenuVar3)
optionMenu3.grid(row=5, column=1, padx=(5, 10), pady=(5, 20), sticky="ew")

centredFrame = customtkinter.CTkFrame(leftFrame, fg_color=leftFrame.cget('fg_color'))
centredFrame.grid(row=6, column=0, padx=0, pady=0, sticky="ew", columnspan=2)
centredFrame.grid_columnconfigure(0, weight=1)

def startSimulation():
    host = socket.gethostname()
    port = 2000
    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server
    data['autonomousVehicleID'] = entry.get()
    client_socket.send(str(data).encode())  # send message
    client_socket.close()  # close the connection
    time.sleep(5)
    app.destroy()

button = customtkinter.CTkButton(centredFrame, text="commancer la simulation", command=startSimulation)
button.grid(row=0, column=0, pady=(10, 30))


rightFrame = customtkinter.CTkFrame(app)
rightFrame.grid(row=0, column=1)
rightFrame.grid_columnconfigure(0, weight=1)
myImage = customtkinter.CTkImage(Image.open('autonomousCar.png'), size=(400, 300))
imageLabel = customtkinter.CTkLabel(rightFrame, image=myImage, text="")
imageLabel.grid(row=0, column=0, padx=10, pady=20)

app.mainloop()