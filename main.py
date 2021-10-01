import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# USER EDITABLE DATA
EXCEL_DATA = '16u-187-0490_DATA.xlsx'
BATTERY_OFFSET_UPPER = [14, 0.311]
BATTERY_OFFSET_LOWER = [12, 0.658]
INJECTOR_DATA_BATTERY = 13.5

if __name__ == '__main__':
    # Open excel sheet of data
    df = pd.read_excel(EXCEL_DATA)
    pulsed_flow_data = df.to_numpy()

    # Calculate nominal battery offset to translate slope to go through the 0,0 point
    # Uses standard linear interpolation from two value points
    nom_slope = (BATTERY_OFFSET_UPPER[1] - BATTERY_OFFSET_LOWER[1]) / (
            BATTERY_OFFSET_UPPER[0] - BATTERY_OFFSET_LOWER[0])
    nom_offset = nom_slope * (INJECTOR_DATA_BATTERY - BATTERY_OFFSET_LOWER[0]) + BATTERY_OFFSET_LOWER[1]

    # Subtract nominal battery offset on each x value
    pulsed_flow_data[:, 0] -= nom_offset

    # Create best fit slope of data from 0,0 and the last data point of injector data
    array_length = np.size(pulsed_flow_data, axis=0)
    rise = pulsed_flow_data[array_length - 1][1]
    run = pulsed_flow_data[array_length - 1][0]
    slope = rise / run

    # Create table of (curve fit) - (actual) to get adder list
    adder_table = []
    for i in pulsed_flow_data:
        adder_table.append([i[0], i[0] * slope - i[1]])

    # .125s increments required for the link ECU up to 4s
    link_table = np.linspace(0.0, 4.0, num=33)
    print(link_table)
    link_values = np.interp(link_table, np.array(adder_table)[:, 0], np.array(adder_table)[:, 1])

    plt.plot(np.array(adder_table)[:, 0], np.array(adder_table)[:, 1], color='g', label='Original Adder')
    plt.plot(link_table, link_values, color='r', label='Interpolated Adder')
    plt.xlabel("PW")
    plt.ylabel("Volumetric")
    plt.title("Injector Calculator")
    plt.legend()
    plt.show()
    # Export to excel table for easy link inputing!
    excel_adder = pd.DataFrame(link_values)
    excel_adder.to_excel('adder_table.xlsx')
    # Export as excel
