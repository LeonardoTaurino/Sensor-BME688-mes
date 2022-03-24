import os
import time
from datetime import datetime
from tkinter import *
from tkinter import messagebox, ttk
from bme68x import BME68X
import bme68xConstants as cnst
import bsecConstants as bsec
import gpiozero as gpio
from time import sleep
from matplotlib import pyplot as plt
import math

bme = BME68X(cnst.BME68X_I2C_ADDR_HIGH, 0) # Create and initialize new BME68X sensor object, initialize I2C interface
bme.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP)
ts=0;
stopVar=False; #to quit from the run
accuracyMinimum=0; #accuracy da raggiungere prima di iniziare misura
val=['sample_nr', 'timestamp', 'iaq', 'iaq_accuracy', 'static_iaq', 'static_iaq_accuracy', 'co2_equivalent', 'co2_accuracy', 'breath_voc_equivalent', 'breath_voc_accuracy', 'raw_temperature', 'raw_pressure', 'raw_humidity', 'raw_gas', 'stabilization_status', 'run_in_status', 'temperature', 'humidity', 'comp_gas_value', 'comp_gas_accuracy', 'gas_percentage', 'gas_percentage_accuracy'];
uni=[" [ ]"," [min]"," [ ]"," [ ]"," [ ]"," [ ]"," [ppm]"," [ ]"," [ppm]"," [ ]"," [°C]"," [hPa]"," [%]"," [kOhm]"," [ ]"," [ ]", " [°C]"," [%]"," [log_10(Ohm)]"," [ ]"," [%]"," [ ]"]
seq=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]; #stabilisco l'ordine di visualizzazione dei dati
#GRAPH VARIABLES------------------------------------------------------------------------------------------------------
n=2 #chose what value to draw in the graph (y only)
graphDraw=str(val[n])
yUnit=str(uni[n])
yGraph=[];
tGraph=[];
plt.ion()
figure, ax = plt.subplots(figsize=(8, 6))
line1, = ax.plot(tGraph,yGraph,'-')
plt.title(graphDraw, fontsize=25)
plt.xlabel("time [min]", fontsize=18)
plt.ylabel(graphDraw + yUnit, fontsize=18)
plt.setp(line1, color='b', linewidth=2.0, marker='.')

def update_progress_label(pb_window): #It Updates progress bar
    return f"Current Progress: {round(pb_window['value'], 1)}%"
def mesure(timeSam):
    try:
        sampleTime = float(timeSam)*60;
    except ValueError:
        print("INSERIRE SOLO NUMERI")
        messagebox.showerror(title="ERRORE", message="Valori dei tempi non validi.")
    check["state"] = DISABLED
    b1_win1["state"] = DISABLED
    e1_win1["state"] = DISABLED
    #wait accuracy
    while True:
        lb2_win1["text"] = "Calibration . ."
        win.update()
        bsec_data = get_data(bme)
        while bsec_data == None:
            bsec_data = get_data(bme)
        #print(bsec_data["iaq_accuracy"])#debug
        lb2_win1["text"] = "Calibration..."
        win.update()
        time.sleep(1)
        if bsec_data["iaq_accuracy"]>= accuracyMinimum:
            lb2_win1["text"] = " "
            win.update()
            break
    global ts
    t_start1 = time.time();
    while time.time() < t_start1 + sampleTime:
        # MISURA DAL SENOSRE----------------------------------------
        t_str_recive=time.time()
        bsec_data = get_data(bme)
        while bsec_data == None:
            bsec_data = get_data(bme)
        if ts==0:    
            ts = bsec_data["timestamp"]*0.000000001
            print(DataOrd(val,uni,seq,"lab",bsec_data)) #label title in shell
        print(DataOrd(val,uni,seq,"data",bsec_data)) #print data
        file.write(DataOrd(val,uni,seq,"data",bsec_data)+ "\n")
        t_end_recive=time.time()
        dt_recive=t_end_recive-t_str_recive
                #---------------------------------------------------GRAPH-----------------------------------------------------
        tGraph.append((bsec_data["timestamp"]*0.000000001-ts)/60)
        yGraph.append(round(bsec_data[graphDraw],2))
        plt.xlim(0, math.floor(max(tGraph)) + 10)
        plt.ylim(0, math.floor(max(yGraph)) + 10)
        line1.set_xdata(tGraph)
        line1.set_ydata(yGraph)
        figure.canvas.draw()
        figure.canvas.flush_events()
        #file.write(str(float(round(time.time() - t_start1,3))) + " | 3213 | 434 | 4324\n"); #DEBUG
        #print(int(time.time() - t_start1))  # DEBUG
        if pb1_win1['value'] < 100: #update progress bar
            pb1_win1['value'] += 100 / (sampleTime / dt_recive)
            lbl_win1['text'] = update_progress_label(pb1_win1)
            lb3_win1['text'] = "Elapsed time: " + str(round((time.time() - t_start1)/60,2)) + " min"
            win.update()
        if stopVar==True:
            plt.savefig("my_plot.png")
            plt.close()
            file.close();
            break
    global dt_end1
    dt_end1= time.time() - t_start1; #save end time for pause loop
    pb1_win1['value'] = 100
    lbl_win1['text'] = f"Current Progress: 100%"
    messagebox.showinfo(message='Sampling complited!')
    b2_win1["state"] = NORMAL
    b3_win1["state"] = DISABLED
    file.close();
def indefTime():
    if e1_win1["state"] == NORMAL:
        e1_win1.delete(0, len(e1_win1.get()));
        e1_win1.insert(END, "44640");
        e1_win1["state"] = DISABLED;
    else:
        e1_win1["state"] = NORMAL;
        e1_win1.delete(0, len(e1_win1.get()));
        e1_win1.insert(END, "0.1");
def stop(window):
    global stopVar;
    stopVar=True;
def endWin(window):
    window.destroy()
def get_data(sensor):
    data = {}
    try:
        data = sensor.get_bsec_data()
    except Exception as e:
        print(e)
        return None
    if data == None or data == {}:
        sleep(0.1)
        return None
    else:
        sleep(3)
        return data
    
def EasyW(bsec_d,dato):
    return str(round(bsec_d[val[dato]],2))

def DataOrd(v,u,s,lab_or_data,bsec_da):
    line=""
    if lab_or_data=="lab":
        for i in range(len(v)):
            if i==0:
                line=v[s[i]]+ u[s[i]]
            else:
                line = line + " | " + v[s[i]]+ u[s[i]]
        return line
    if lab_or_data=="data":
        datline=""
        for j in range(len(v)):
            if j==0:
                datline=EasyW(bsec_da,s[j])
            if j==1:
                datline= datline + " | " + str(round((bsec_da["timestamp"]*0.000000001-ts)/60,3))
            if j>1:
                datline= datline + " | " + EasyW(bsec_da, s[j])
        return datline

# take date to store files:
now = datetime.now();
nowStr = now.strftime("%d_%m_%Y %H_%M_%S");
# Open file to write in
fileName = "Prova " + nowStr + ".txt";
path = '/home/pi/Desktop/Sensor Mesures/';
file = open(path + fileName, 'w');
file.write(DataOrd(val,uni,seq,"lab",None) + "\n");

win = Tk();
win.title("SENSORE ODORI");
lbl1_win1 = Label(win, text="Set time [min]: ").grid(row=0, column=0);
e1_win1 = Entry(win, width=20);
e1_win1.grid(row=0, column=1);
e1_win1.insert(END, "1");
b1_win1 = Button(win, state=NORMAL, text="Start", command=lambda: mesure(e1_win1.get()), width=12, height=1, fg="green");
b1_win1.grid(row=0, column=3);
pb1_win1 = ttk.Progressbar(win, orient='horizontal', mode='determinate', length=280);
pb1_win1.grid(column=0, row=4, columnspan=3)
lbl_win1 = ttk.Label(win, text=update_progress_label(pb1_win1))
lbl_win1.grid(column=0, row=3, columnspan=3)
lb2_win1 = Label(win, text=" ")
lb2_win1.grid(column=0, row=2, columnspan=4)
lb3_win1 = ttk.Label(win, text="time")
lb3_win1.grid(column=0, row=5, columnspan=3)
b2_win1 = Button(win, state=DISABLED, text="Quit", command=lambda: endWin(win), width=12)
b2_win1.grid(row=5, column=3)
var=IntVar();
check=Checkbutton(win, variable=var, text="31 day time",  command=lambda:indefTime())
check.grid(row=0, column=2)
b3_win1 = Button(win, state=NORMAL, text="STOP", command=lambda: stop(win), width=12, fg="red")
b3_win1.grid(row=1, column=3)
win.mainloop()
plt.close()
file.close();