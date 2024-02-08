# make_graphs.py

import random
from matplotlib import pyplot as plt
import batman
import numpy as np
import math
from utilities import add_blank_characters
from formatting import format_multiple_choice
from utilities import select_random_items_from_list

def generate_transit_graph(fixed_planet_parameters,fixed_graph_parameters,zoom_level,labels,filename):

    #label_colors = ['#d73027','#fc8d59','#fee090','#91bfdb','#4575b4','#d73027','#fc8d59','#fee090','#91bfdb','#4575b4','#d73027','#fc8d59','#fee090','#91bfdb','#4575b4']
    #safe_colors = ['#d73927','#f46d43','#74add1','#fdae61','#4575b4','#adb9e9','#ffee09']
    
    #safe_colors = ["#000000", "#555555", "#AAAAAA", "#000080", "#87CEEB", "#8B0000", "#FFA500", "#FFB6C1", "#006400"]

    #fixed_safe_colors = ["#88CCEE", "#CC6677", "#DDCC77", "#117733", "#332288", "#AA4499","#44AA99", "#999933", "#661100", "#000000", "#888888"]
    fixed_safe_colors = ["#2166AC","#B2182B","#4393C3","#D6604D","#92C5DE","#F4A582","#444444"]
    symbol_styles = ["o","v","s","x","+","*","D",">"]
    line_styles = ['dashdot','dashed','solid','dotted','solid','dashed','dashdot','dashed','solid','solid']
    planet_labels = ["A","B","C","D","E","F","G","H","I","J","K"]

    # Randomize the colors used for each instance of the question, so we don't accidentally wind up with the correct answer always having the same color.
    
    new_starting_index = random.randrange(len(fixed_safe_colors))
    safe_colors = fixed_safe_colors[new_starting_index:] + fixed_safe_colors[:new_starting_index]

    # Better to shuffle the array while preserving the order, so similar colors remain widely separated

    num_points = int(fixed_graph_parameters['num_points'])

    # Define the axes of the plot
    fig,ax = plt.subplots()

    # Compute the models depending on the number of planets passed in and the zoom level.
    if len(fixed_planet_parameters) == 1:
        '''Only a single planet has been supplied, so constructing the graph is very simple. No labels are required.'''

        # Determine the time range for the graph depending on whether we are making a close-up of a transit or a multi-period plot
        if zoom_level == "single_transit":
            print("orbital period ",fixed_planet_parameters[0]['orbital_period'])
            print("planet radius ",fixed_planet_parameters[0]['planet_radius'])
            print("nominal transit depth",1-fixed_planet_parameters[0]['planet_radius']**2)
            current_planet_transit_duration = get_transit_duration(fixed_planet_parameters[0]['orbital_period'],1.0,fixed_planet_parameters[0]['planet_radius'],fixed_planet_parameters[0]['orbital_eccentricity'],semi_major_axis=fixed_planet_parameters[0].get('orbital_semimajor_axis',10.0))
            time_start = fixed_planet_parameters[0].get('inferior_conjunction',0)+ current_planet_transit_duration/2.0
            time_end = fixed_planet_parameters[0].get('inferior_conjunction',0) - current_planet_transit_duration/2.0

            # time_start = -fixed_planet_parameters[0]['orbital_period']/50.0
            # time_end = fixed_planet_parameters[0]['orbital_period']/50.0
        elif zoom_level == "multi_transit":
            time_start = -fixed_planet_parameters[0]['orbital_period']*random.uniform(0.5,1.0)
            time_end = fixed_planet_parameters[0]['orbital_period']*random.uniform(3.1,4.2)
        else:
            time_start = 0.5
            time_end = -0.5

        # Choose times spaced evenly through an interval, then displace them randomly.
        # With a sufficient density of points, this guarantees that every transit will be sampled
        times = np.linspace(time_start, time_end, num_points)
        random_times = np.array([time*random.uniform(0.8,1.2) for time in times])
    
        fluxes = make_transit_light_curve(random_times,fixed_planet_parameters[0]['orbital_period'],fixed_planet_parameters[0]['planet_radius'],\
            orbital_eccentricity=fixed_planet_parameters[0].get('orbital_eccentricity',0),time_inferior_conjunction=fixed_planet_parameters[0].get('inferior_conjunction',0),orbital_semimajor_axis=fixed_planet_parameters[0].get('orbital_semimajor_axis',10.0))
        flux_with_noise = add_noise(fluxes,fixed_graph_parameters['noise_level'])
        plt.scatter(random_times, flux_with_noise)

        
    elif (len(fixed_planet_parameters) > 1) and (zoom_level == "multi_transit"):
        '''This is a multi-planet graph showing multiple transits. Therefore, stack the light curves to combine them.
        Calculate the model and fluxes for each planet, subtract one from the fluxes, than add the resulting decrements together. 
        This is not suitable for research, because it doesn't accurately account for planets that overlap while transiting.
        But it should be okay as a first stab.'''

        # Find the planet with the largest period and use its period to set the time range for the graph.
        periods = [fixed_planet_parameters[i]['orbital_period'] for i in range(0,len(fixed_planet_parameters))]

        # Set the time range for the graph appropriate to a multi-transit graph, ensuring that we would see three periods 
        # of the longest-period planet (unless the time of inferior conjunction were set to a very large fraction of a period)
        time_start = -max(periods)*random.uniform(0.1,0.1)
        time_end = max(periods)*random.uniform(4.1,4.5)
        
        # Choose times spaced evenly through an interval, then displace them randomly.
        # With a sufficient density of points, this guarantees that every transit will be sampled
        times = np.linspace(time_start, time_end, num_points)
        random_times = np.array([time*random.uniform(0.8,1.2) for time in times])

        # Loop through the planets and calculate their contributions to the light curve
        cumulative_decrements = [0 for i in range(0,num_points)]
        time_labels = []

        for i in range(0,len(fixed_planet_parameters)):

            # Check whether the user has specified a range of inferior conjunction values and, if not, set it to zero
            #print('Time of inferior conjunction, period = ',current_planet_params.t0,current_planet_params.per)
            
            current_planet_fluxes = make_transit_light_curve(random_times,fixed_planet_parameters[i]['orbital_period'],fixed_planet_parameters[i]['planet_radius'],\
                orbital_eccentricity=fixed_planet_parameters[i].get('orbital_eccentricity',0),time_inferior_conjunction=fixed_planet_parameters[i].get('inferior_conjunction',0),orbital_semimajor_axis=fixed_planet_parameters[i].get('orbital_semimajor_axis',10.0))
            time_labels.append([fixed_planet_parameters[i].get('inferior_conjunction',0),fixed_planet_parameters[i]['orbital_period']])
            current_planet_decrements = [(1 - current_planet_fluxes[i]) for i in range(0,num_points)]
            cumulative_decrements = [(cumulative_decrements[i] + current_planet_decrements[i]) for i in range(0,num_points)]

        fluxes = [(1-cumulative_decrements[i]) for i in range(0,len(cumulative_decrements))]
        flux_with_noise = add_noise(fluxes,fixed_graph_parameters['noise_level'])
        plt.scatter(random_times, flux_with_noise, s = 5)

        # Add labels to the planets.

        # Get the limits of the graph before we start adding elements so that we can correctly 
        # space the labels without the spacing added as the graph limits increase
        ymin, ymax = ax.get_ylim()
        if labels:
            # As this is a multi-period graph, add labels along the top of the graph for maximum disambiguation.
            for k in range(0,len(fixed_planet_parameters)):
                time_labels_this_planet = []
                # Make a list of transits of this planet that fit within the graph range:
                time_label_this_planet_new = 0
                i = 0
                while time_label_this_planet_new < (time_end-time_labels[k][1]):
                    time_label_this_planet_new = time_labels[k][0]+i*time_labels[k][1]
                    time_labels_this_planet.append(time_label_this_planet_new)
                    i += 1
                # Randomly select three labels to keep for each planet. This helps with label crowding.
                random.shuffle(time_labels_this_planet)
                time_labels_this_planet = time_labels_this_planet[:4]

                # Set the height of the labels to be a fixed fraction of the height of the viewport,             
                # chosen to work reasonably well with all but the very highest noise levels.

                label_y_location = 1.0+fixed_graph_parameters['noise_level']*5 + k*(ymax-ymin)/15
                for time_label in time_labels_this_planet:
                    # print("time label ",time_label)
                    ax.text(time_label, label_y_location, planet_labels[k], color=safe_colors[k],fontsize='14',fontweight='bold',horizontalalignment='center',verticalalignment='bottom')
                    ax.vlines(time_label,ymin=ymin,ymax=label_y_location,color=safe_colors[k],linestyle=line_styles[k],linewidth=1.2, zorder=0)
        
            # Manually boost the ylim to ensure the topmost labels don't intersect the top border:
            current_ylims = ax.get_ylim()
            # print("current_ylims = ",current_ylims)
            ax.set_ylim(current_ylims[0],current_ylims[1]+((current_ylims[1]-current_ylims[0])/30))


    elif (len(fixed_planet_parameters) > 1) and (zoom_level == "single_transit"):
        '''We are making multiple light curves, but looking at a single transit of each planet, all overlapping.
        Therefore, don't combine the light curves into a single curve. Render each one separately in a different color and label them separately.'''

        # Set the time limits for the graph. Focus on the area around a single transit.
        time_start = -0.05
        time_end = 0.05

        # Loop through the transit durations and inferior conjunction times of the planets to find the time range for the graph

        max_time_range_high_all_planets = 0
        max_time_range_low_all_planets = 0
        for i in range(0,len(fixed_planet_parameters)):
            current_planet_transit_duration = get_transit_duration(fixed_planet_parameters[i]['orbital_period'],1.0,fixed_planet_parameters[i]['planet_radius'],fixed_planet_parameters[i]['orbital_eccentricity'],semi_major_axis=fixed_planet_parameters[i].get('orbital_semimajor_axis',10.0))
            time_range_high = fixed_planet_parameters[i].get('inferior_conjunction',0)+ current_planet_transit_duration/2.0
            time_range_low = fixed_planet_parameters[i].get('inferior_conjunction',0) - current_planet_transit_duration/2.0
            #time_range_max = (time_range_high if abs(time_range_high) > abs(time_range_low) else time_range_low)
            if time_range_high > max_time_range_high_all_planets: max_time_range_high_all_planets = time_range_high
            if time_range_low < max_time_range_low_all_planets: max_time_range_low_all_planets = time_range_low
        
        # print("max range high",max_time_range_high_all_planets)
        # print("max range low",max_time_range_low_all_planets)

        time_range = time_end - time_start
        time_start = (max_time_range_low_all_planets + time_range*0.2 if max_time_range_low_all_planets > 0 else max_time_range_low_all_planets - time_range*0.2)
        time_end = (max_time_range_high_all_planets + time_range*0.2 if max_time_range_high_all_planets > 0 else max_time_range_high_all_planets - time_range*0.2)

        # For realism, randomly space out the times sampled.
        times = np.linspace(time_start, time_end, num_points)
        random_times = np.array([time*random.uniform(0.9,1.1) for time in times])

        # Loop through the planets and calculate their light curves
        cumulative_decrements = [0 for i in range(0,num_points)]
        for i in range(0,len(fixed_planet_parameters)):
            # Check whether the user has specified a range of inferior conjunction values and, if not, set it to zero
            current_planet_fluxes = make_transit_light_curve(random_times,fixed_planet_parameters[i]['orbital_period'],fixed_planet_parameters[i]['planet_radius'],\
                orbital_eccentricity=fixed_planet_parameters[i].get('orbital_eccentricity',0),time_inferior_conjunction=fixed_planet_parameters[i].get('inferior_conjunction',0),orbital_semimajor_axis=fixed_planet_parameters[i].get('orbital_semimajor_axis',10.0))
           
            flux_with_noise = add_noise(current_planet_fluxes,fixed_graph_parameters['noise_level'])
            plt.scatter(random_times, flux_with_noise, color=safe_colors[i],marker=symbol_styles[i], s = 15,label=planet_labels[i])

    # Assemble the final figure
    
    plt.xlabel("Time (years)")
    plt.ylabel("Relative brightness (host star brightness units)")
    handles,labels = ax.get_legend_handles_labels()
    if len(labels) > 0:
        ax.legend()
    # plt.legend()
    plt.savefig(filename)
    plt.close('all')
    return 

def make_transit_light_curve(sample_times,orbital_period,planet_radius,orbital_eccentricity=0.0,time_inferior_conjunction=0.0,orbital_semimajor_axis=10.0):

    params = batman.TransitParams()
    params.t0 = time_inferior_conjunction       # type: ignore #time of inferior conjunction
    params.per = orbital_period                 #orbital period
    params.rp = planet_radius                   #planet radius (in units of stellar radii)
    params.a = orbital_semimajor_axis           # type: ignore #semi-major axis (in units of stellar radii)
    params.inc = 90.                            # type: ignore #orbital inclination (in degrees)
    params.ecc = orbital_eccentricity           # type: ignore #eccentricity
    params.w = 90.                              # type: ignore #longitude of periastron (in degrees)
    params.u = [0.1,0.2]                       # type: ignore #limb darkening coefficients [u1, u2]
    params.limb_dark = "quadratic"              # type: ignore #limb darkening model
       
    planet_model = batman.TransitModel(params, sample_times)    #initializes model
    planet_fluxes = planet_model.light_curve(params)          #calculates light curve
 
    return planet_fluxes

def add_noise(fluxes,noise_level):

    # Add Gaussian random noise to the flux measurements. The standard deviation will be the specified noise level
    gaussian_noise = np.random.normal(0, noise_level, len(fluxes))
    flux_with_noise = fluxes + gaussian_noise
    return flux_with_noise

def get_transit_duration(orbital_period,radius_star,radius_planet,orbital_eccentricity,semi_major_axis):

    # This formula only works for small orbital eccentricity. It will fail for eccentricities closer to 1.0
    duration = orbital_period*(radius_star + radius_planet)/(math.pi*semi_major_axis*(1-orbital_eccentricity**2)**(-0.5))
    return duration


