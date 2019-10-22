#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

hsrlca.calc: High-speed rail life cycle assessment calculations
===============================================================

hsrlca.calc provides requisite functions for stepwise construction of a high-
speed rail life cycle assessment model, as designed for research on Chinese 
rail development in continental Southeast Asia. It provides for dynamic 
modeling of trade arrangements and national energy mix scenarios.

The functions of this module are, at present, specific to six countries and 
require inputs of the same format as included in the hsrlca package's example 
documents. Should this project evolve in the future, the first aim will be to 
increase generalizability to other scenarios.

Dependencies
------------
numpy
pandas

'''

import numpy as np
import pandas as pd

def tradeSchedule(home_country, up_countries, up_inputs_base):
    '''Creates a trade schedule given the specified home country and the 
    countries in which various unit processes occur.'''
    
    # Extract list of unit processes from master unit process dataset
    up_list = pd.DataFrame({'unit_process': up_inputs_base['unit_process']})
    
    # Fill home_country column for every unit process row in up_list
    home_list = pd.DataFrame({'home_country': [home_country]*len(up_list)},
                            index = up_list['unit_process'])
    
    # Check up_countries index and set to up_list values if not already same
    up_index = pd.Index(up_list)
    up_countries_idx = up_countries.index
    if not up_countries_idx.equals(up_index):
        up_countries.index = up_list['unit_process']
        up_countries.drop('unit_process', axis=1, inplace=True)
    
    # Concatenate with the list of producing countries to provide a trade schedule
    trade_schedule = pd.concat([home_list, up_countries], axis=1)

    return trade_schedule

def transportSchedule(trade_schedule, trade_distances, up_inputs_base):
    '''Creates a pandas dataframe containing estimated average transport 
    distances, covering all possible routes.'''
    
    # Extract list of unit processes from master unit process dataset
    up_list = pd.DataFrame({'unit_process': up_inputs_base['unit_process']})

    # Map distances to the trade schedule found via tradeSchedule(...)
    transport_schedule = pd.merge(trade_schedule, trade_distances, how='left', on=['home_country', 'up_countries'])
    
    # Set index to unit processes
    transport_schedule.index = up_list['unit_process']
    
    return transport_schedule

def transportUpdate(transport_schedule, up_inputs_base, rail_allocation=0.5):
    '''Updates the given inputs dataframe with calculated transport requirements.'''
    
    # Extract transport_distances
    transport_distances = pd.DataFrame(transport_schedule['avg_export_distance'])
    
    # Mask unit processes that do not entail transportation by setting value to 0
    no_transport = ['electricity_Cambodia_kWh',
                    'electricity_China_kWh',
                    'electricity_LaoPDR_kWh',
                    'electricity_Myanmar_kWh',
                    'electricity_Thailand_kWh',
                    'electricity_Vietnam_kWh',
                    'lorry_raw_material_transport_kg-km',
                    'rail_raw_material_transport_kg-km',
                    'lorry_intermediate_component_transport_kg-km',
                    'rail_intermediate_component_transport_kg-km',
                    'lorry_final_component_transport_kg-km',
                    'rail_final_component_transport_kg-km',
                    'high_speed_rail_operation_p-km'
                   ]
    for unit_process in no_transport:
        transport_distances.loc[unit_process] = 0
    
    # Create copy of up_inputs_base for transformation
    up_inputs_transport_update = up_inputs_base.copy()
    
    # Set up_inputs_base indices
    up_inputs_transport_update.set_index(['phase', 'unit_process'], inplace=True)
    
    for up in transport_distances.index:
        if up_inputs_transport_update.xs(up, level = 1, drop_level=False).index[0][0] == "raw_material_extraction":
            up_inputs_transport_update.loc['raw_material_extraction', up]['lorry_raw_material_transport_kg-km'] = (1 - rail_allocation) * transport_distances.loc[up]['avg_export_distance']
            up_inputs_transport_update.loc['raw_material_extraction', up]['rail_raw_material_transport_kg-km'] = rail_allocation * transport_distances.loc[up]['avg_export_distance']
        elif up_inputs_transport_update.xs(up, level = 1, drop_level=False).index[0][0] == "intermediate_component_production_i":
            up_inputs_transport_update.loc['intermediate_component_production_i', up]['lorry_intermediate_component_transport_kg-km'] = (1 - rail_allocation) * transport_distances.loc[up]['avg_export_distance']
            up_inputs_transport_update.loc['intermediate_component_production_i', up]['rail_intermediate_component_transport_kg-km'] = rail_allocation * transport_distances.loc[up]['avg_export_distance']
        elif up_inputs_transport_update.xs(up, level = 1, drop_level=False).index[0][0] == "intermediate_component_production_ii":
            up_inputs_transport_update.loc['intermediate_component_production_ii', up]['lorry_intermediate_component_transport_kg-km'] = (1 - rail_allocation) * transport_distances.loc[up]['avg_export_distance']
            up_inputs_transport_update.loc['intermediate_component_production_ii', up]['rail_intermediate_component_transport_kg-km'] = rail_allocation * transport_distances.loc[up]['avg_export_distance']
        elif up_inputs_transport_update.xs(up, level = 1, drop_level=False).index[0][0] == "final_component_production":
            up_inputs_transport_update.loc['final_component_production', up]['lorry_final_component_transport_kg-km'] = (1 - rail_allocation) * transport_distances.loc[up]['avg_export_distance']
            up_inputs_transport_update.loc['final_component_production', up]['rail_final_component_transport_kg-km'] = rail_allocation * transport_distances.loc[up]['avg_export_distance']
    
    return up_inputs_transport_update

def energyMixes(national_energy_supply):
    '''Creates a dataframe containing percentage energy mixes for each country
    from given raw values.'''
    
    import numpy as np
    
    # Create national_energy_mixes dataframe
    national_energy_mixes = national_energy_supply.copy()

    # Set country column as index
    national_energy_mixes.set_index('country', drop=True, inplace=True)

    # Calculate country energy totals
    national_energy_mixes['total_gw'] = national_energy_mixes.sum(axis=1)

    # Prepare column names
    national_energy_mixes.columns = national_energy_mixes.columns.str.rstrip('_gw')    

    # Tabulate % energy mix by fuel type and assign to new "% Total" columns
    for col in national_energy_mixes:
        national_energy_mixes[col + "_pct_total"] = national_energy_mixes[col] / national_energy_mixes['total']

    # Remove raw values
    national_energy_mixes.drop(national_energy_mixes.iloc[:,0:8], axis=1, inplace=True)

    # Confirm totals add up to 100% and, if so, remove totals column
    if np.mean(national_energy_mixes['total_pct_total']) == 1.0:
        national_energy_mixes.drop('total_pct_total', axis=1, inplace=True)
    else:
        print('Please check energy mix calculations; totals did not all add up to 100%')
    
    return national_energy_mixes

def energyMixEmissions(national_energy_mixes, unit_energy_emissions):
    '''Calculates unit energy emissions, returning in a new dataframe.'''
    
    # Set unit_energy_emissions index to 'fuel'
    unit_energy_emissions.set_index('fuel', inplace=True)
    
    # Prepare national_energy_mixes column names for dot product with unit_energy_emissions
    national_energy_mixes.columns = unit_energy_emissions.index
    
    # Take dot product to calculate energy_mix_emissions (per kWh)
    energy_mix_emissions = national_energy_mixes.dot(unit_energy_emissions)
    
    return energy_mix_emissions

def energyMixEmissionsUpdate(up_emissions_base, energy_mix_emissions):
    '''Updates the base emissions dataset with national unit energy emissions,
    returning in a new dataframe.'''
    
    # Create up_emissions_complete dataframe
    up_emissions_complete = up_emissions_base.copy()
    
    # Prepare up_emissions_complete index
    up_emissions_complete.set_index(['phase', 'unit_process'], inplace=True)
    
    # Update up_emissions_complete values for electricity generation with energy_mix_emissions
    up_emissions_complete.loc['electricity_generation'] = energy_mix_emissions.get_values()
    
    return up_emissions_complete

def electricitySourceUpdate(up_inputs_transport_update, trade_schedule):
    '''Updates the dataset with the source of electricity required for each 
    unit process, as dictated by the trade scenario.'''
    
    # Create up_inputs_elec_update dataframe
    up_inputs_elec_update = up_inputs_transport_update.copy()
    
    # For all unit processes not in the electricity generation phase, allocate electricity requirements to the country indicated by the trade schedule; if moved from first col, replace first col value with 0
    for up in up_inputs_elec_update.index.get_level_values('unit_process').unique():
        if up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up].index[0] != 'electricity_generation':
            if trade_schedule.loc[up][1] == 'Cambodia':
                pass
            elif trade_schedule.loc[up][1] == 'China':
                up_inputs_elec_update['electricity_China_kWh'].loc[:, up] = up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up][0]
                up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up] = 0
            elif trade_schedule.loc[up][1] == 'LaoPDR':
                up_inputs_elec_update['electricity_LaoPDR_kWh'].loc[:, up] = up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up][0]
                up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up] = 0
            elif trade_schedule.loc[up][1] == 'Myanmar':
                up_inputs_elec_update['electricity_Myanmar_kWh'].loc[:, up] = up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up][0]
                up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up] = 0
            elif trade_schedule.loc[up][1] == 'Thailand':
                up_inputs_elec_update['electricity_Thailand_kWh'].loc[:, up] = up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up][0]
                up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up] = 0
            elif trade_schedule.loc[up][1] == 'Vietnam':
                up_inputs_elec_update['electricity_Vietnam_kWh'].loc[:, up] = up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up][0]
                up_inputs_elec_update['electricity_Cambodia_kWh'].loc[:, up] = 0
    
    return up_inputs_elec_update

def passengerUpdate(up_inputs_elec_update, **norm_params):
    '''Calculates passenger transportation requirements, relating them to one 
    functional unit (1 p*km) based on the input assumptions list, updating a 
    copy of the dataset.
    
    The assumed input dataframe (default 'up_inputs_complete') displays the 
    requirements for ONE UNIT (with units specified in the process name); only
    the final element, passenger transportation, is listed in terms of the 
    functional unit at this stage.
    
    The function only uses a subset of the norm_params keys, but calling the 
    full dictionary simplifies user input.
    '''
    
    # Define passenger transportation unit process requirements, defined to yield passenger transportation output of 1 p*km
    trainCar_req = 1/(norm_params['atc']*norm_params['atcf']*norm_params['adt']*norm_params['attd']*norm_params['anat']*norm_params['days']*norm_params['atl']) # 1 / (average train capacity * average % capacity filled * average daily trips per train * average train trip distance * average number of active trains * days in year * average train lifespan)
    ballastedTrack_req = 1*norm_params['apbt']/(norm_params['atc']*norm_params['atcf']*norm_params['adt']*norm_params['attd']*norm_params['anat']*norm_params['days']*norm_params['ail']) # 1 (km) * % ballasted track / (average train capacity * average % capacity filled * average daily trips per train * average train trip distance * days in year * average infrastructure lifespan)
    nonballastedTrack_req = 1*norm_params['apnt']/(norm_params['atc']*norm_params['atcf']*norm_params['adt']*norm_params['attd']*norm_params['anat']*norm_params['days']*norm_params['ail']) # 1 (km) * % nonballasted track / (average train capacity * average % capacity filled * average daily trips per train * average train trip distance * days in year * average infrastructure life life)
    reqTrackSystems_req = 1/(norm_params['atc']*norm_params['atcf']*norm_params['adt']*norm_params['attd']*norm_params['anat']*norm_params['days']*norm_params['ail']) # 1 (km of track systems) / (average train capacity * average % capacity filled * average daily trips per train * average train trip distance * days in year * average infrastructure life)
    
    # Create working copy of unit process dataset
    up_inputs_complete = up_inputs_elec_update.copy()
    
    # Update relevant unit processes according to the above calculations
    up_inputs_complete.loc['passenger_transportation', 'high_speed_rail_operation_p-km']['high_speed_train_car_n'] = trainCar_req
    up_inputs_complete.loc['passenger_transportation', 'high_speed_rail_operation_p-km']['ballasted_track_km'] = ballastedTrack_req
    up_inputs_complete.loc['passenger_transportation', 'high_speed_rail_operation_p-km']['non-ballasted_track_km'] = nonballastedTrack_req
    up_inputs_complete.loc['passenger_transportation', 'high_speed_rail_operation_p-km']['requisite_track_systems_km'] = reqTrackSystems_req
    
    return up_inputs_complete

def totalRequirements(up_inputs_complete):
    '''Calculates the total materials required to produce one unit of train 
    operations in terms of the functional unit (1 p*km).
    
    To calculate requirements, the function 'backpropagates' the inputs used 
    in successive phases, proceeding stepwise from the final to initial phase.
    '''

    # Create up_total_requirements dataframe
    up_total_requirements = up_inputs_complete.copy()

    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['final_component_production'].index: # Selects all unit processes in parent phase
        # Initialize counter that tracks total requirements in parent phase
        subtotal_final_component_production = 0
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['passenger_transportation'][up].index: # Slices phase and column
            subtotal_final_component_production += up_total_requirements.loc['passenger_transportation'][up][entry]
        # Calculate total requirements
        up_total_requirements.loc[('final_component_production', up)] = up_inputs_complete.loc[('final_component_production', up)] * subtotal_final_component_production
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_final_component_production = 0
    
    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['final_component_transportation'].index:
        # Initialize counter that tracks total requirements in parent phase
        subtotal_final_component_transportation = 0
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['final_component_production'][up].index: # Slices phase and column
            subtotal_final_component_transportation += up_total_requirements.loc['final_component_production'][up][entry]
        up_total_requirements.loc[('final_component_transportation', up)] = up_inputs_complete.loc[('final_component_transportation', up)] * subtotal_final_component_transportation
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_final_component_transportation = 0

    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['intermediate_component_production_ii'].index:
        # Initialize counter that tracks total requirements in parent phase
        subtotal_intermediate_component_production_ii = 0
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['final_component_production'][up].index: # Slices phase and column
            subtotal_intermediate_component_production_ii += up_total_requirements.loc['final_component_production'][up][entry]
        for entry in up_total_requirements.loc['passenger_transportation'][up].index: # Slices phase and column
            subtotal_intermediate_component_production_ii += up_total_requirements.loc['passenger_transportation'][up][entry]
        # Calculate total requirements
        up_total_requirements.loc[('intermediate_component_production_ii', up)] = up_inputs_complete.loc[('intermediate_component_production_ii', up)] * subtotal_intermediate_component_production_ii
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_intermediate_component_production_ii = 0

    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['intermediate_component_production_i'].index:
        subtotal_intermediate_component_production_i = 0 # Initialize counter that tracks total requirements in parent phase
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['intermediate_component_production_ii'][up].index: # Slices phase and column
            subtotal_intermediate_component_production_i += up_total_requirements.loc['intermediate_component_production_ii'][up][entry]
        for entry in up_total_requirements.loc['final_component_production'][up].index: # Slices phase and column
            subtotal_intermediate_component_production_i += up_total_requirements.loc['final_component_production'][up][entry]
        for entry in up_total_requirements.loc['passenger_transportation'][up].index: # Slices phase and column
            subtotal_intermediate_component_production_i += up_total_requirements.loc['passenger_transportation'][up][entry]
        # Calculate total requirements
        up_total_requirements.loc[('intermediate_component_production_i', up)] = up_inputs_complete.loc[('intermediate_component_production_i', up)] * subtotal_intermediate_component_production_i
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_intermediate_component_production_i = 0

    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['intermediate_component_transportation'].index:
        subtotal_intermediate_component_transportation = 0 # Initialize counter that tracks total requirements in parent phase
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['intermediate_component_production_i'][up].index: # Slices phase and column
            subtotal_intermediate_component_transportation += up_total_requirements.loc['intermediate_component_production_i'][up][entry]
        for entry in up_total_requirements.loc['intermediate_component_production_ii'][up].index: # Slices phase and column
            subtotal_intermediate_component_transportation += up_total_requirements.loc['intermediate_component_production_ii'][up][entry]
        # Calculate total requirements
        up_total_requirements.loc[('intermediate_component_transportation', up)] = up_inputs_complete.loc[('intermediate_component_transportation', up)] * subtotal_intermediate_component_transportation
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_intermediate_component_transportation = 0

    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['raw_material_extraction'].index:
        # Initialize counter that tracks total requirements in parent phase
        subtotal_raw_material_extraction = 0
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['intermediate_component_production_i'][up].index: # Slices phase and column
            subtotal_raw_material_extraction += up_total_requirements.loc['intermediate_component_production_i'][up][entry]
        for entry in up_total_requirements.loc['intermediate_component_production_ii'][up].index: # Slices phase and column
            subtotal_raw_material_extraction += up_total_requirements.loc['intermediate_component_production_ii'][up][entry]
        for entry in up_total_requirements.loc['final_component_production'][up].index: # Slices phase and column
            subtotal_raw_material_extraction += up_total_requirements.loc['final_component_production'][up][entry]
        for entry in up_total_requirements.loc['passenger_transportation'][up].index: # Slices phase and column
            subtotal_raw_material_extraction += up_total_requirements.loc['passenger_transportation'][up][entry]
        # Calculate total requirements
        up_total_requirements.loc[('raw_material_extraction', up)] = up_inputs_complete.loc[('raw_material_extraction', up)] * subtotal_raw_material_extraction
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_raw_material_extraction = 0

    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['raw_material_transportation'].index:
        # Initialize counter that tracks total requirements in parent phase
        subtotal_raw_material_transportation = 0
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['raw_material_extraction'][up].index: # Slices phase and column
            subtotal_raw_material_transportation += up_total_requirements.loc['raw_material_extraction'][up][entry]
        # Calculate total requirements
        up_total_requirements.loc[('raw_material_transportation', up)] = up_inputs_complete.loc[('raw_material_transportation', up)] * subtotal_raw_material_transportation
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_raw_material_transportation = 0
        
    # Tally total unit process requirements, moving from final to initial phase (where final phase gives requirements for 1 p*km)
    for up in up_total_requirements.loc['electricity_generation'].index:
        # Initialize counter that tracks total requirements in parent phase
        subtotal_electricity_generation = 0
        # Add up required amounts from each entry in each successive phase
        for entry in up_total_requirements.loc['raw_material_extraction'][up].index: # Slices phase and column
            subtotal_electricity_generation += up_total_requirements.loc['raw_material_extraction'][up][entry]
        for entry in up_total_requirements.loc['intermediate_component_production_i'][up].index: # Slices phase and column
            subtotal_electricity_generation += up_total_requirements.loc['intermediate_component_production_i'][up][entry]
        for entry in up_total_requirements.loc['intermediate_component_production_ii'][up].index: # Slices phase and column
            subtotal_electricity_generation += up_total_requirements.loc['intermediate_component_production_ii'][up][entry]
        for entry in up_total_requirements.loc['final_component_production'][up].index: # Slices phase and column
            subtotal_electricity_generation += up_total_requirements.loc['final_component_production'][up][entry]
        for entry in up_total_requirements.loc['passenger_transportation'][up].index: # Slices phase and column
            subtotal_electricity_generation += up_total_requirements.loc['passenger_transportation'][up][entry]
        # Calculate total requirements
        up_total_requirements.loc[('electricity_generation', up)] = up_inputs_complete.loc[('electricity_generation', up)] * subtotal_electricity_generation
        # Reset counter (intended redundancy to safeguard against misuse outside of loop)
        subtotal_electricity_generation = 0

    return up_total_requirements

def calculateEmissionsSchedule(up_inputs_complete, up_emissions_complete):
    '''Calculates the emissions associated with one unit of each unit process,
    sorted by phase, returning in a new dataframe.'''
    
    # Create working copy of up_emissions_complete
    up_emissions = up_emissions_complete.copy()
    
    # Remove MultiIndex on up_emissions to allow dot product; keep on up_inputs_complete for final results   
    up_emissions.reset_index(level='phase', inplace=True)
    up_emissions.drop('phase', axis=1, inplace=True)
    
    # Calculate the emissions_report
    emissions_schedule = up_inputs_complete.dot(up_emissions)
    
    return emissions_schedule

def calculateEmissionsTotal(up_total_requirements, emissions_schedule):
    '''Calculates the total emissions associated with a single p*km of 
    passenger transportation, sorted by phase and unit process.'''
    
    # Create working copy of up_emissions_complete
    up_emissions = emissions_schedule.copy()
    
    # Remove MultiIndex on up_emissions to allow dot product; keep on up_total_requirements for final results   
    up_emissions.reset_index(level='phase', inplace=True)
    up_emissions.drop('phase', axis=1, inplace=True)
    
    # Calculate the total emissions_report
    emissions_total = up_total_requirements.dot(up_emissions)
    
    return emissions_total

def sumPhases(emissions_total):
    '''Sums the total emissions of each phase, reporting subtotals associated 
    with a single p*km of passenger transportation.'''
    
    # Define phase order (including all calculated phases)
    phase_order = ['electricity_generation',
                        'raw_material_extraction',
                        'raw_material_transportation',
                        'intermediate_component_production_i',
                        'intermediate_component_production_ii',
                        'intermediate_component_transportation',
                        'final_component_production',
                        'final_component_transportation',
                        'passenger_transportation']
    
    # Calculate phase totals by grouping items and summing groups
    phase_summary_complete = emissions_total.groupby('phase').sum().reindex(phase_order)
    
    return phase_summary_complete

def condensePhaseSums(phase_summary_complete, home_country):
    '''Combines raw phase subtotals into final desired summary phase totals
    and appends home_country to row labels for cross-country analysis.'''
    
    # Name final combined phases
    phase1_label = "materials_extraction" + '_' + home_country
    phase2_label = "construction" + '_' + home_country
    phase3_label = "operation" + '_' + home_country
    
    # Calculate final combined phase totals
    phase1 = sum([phase_summary_complete.loc['raw_material_extraction'],
                  phase_summary_complete.loc['raw_material_transportation']])
    phase2 = sum([phase_summary_complete.loc['intermediate_component_production_i'],
                  phase_summary_complete.loc['intermediate_component_production_ii'],
                  phase_summary_complete.loc['intermediate_component_transportation'],
                  phase_summary_complete.loc['final_component_production'],
                  phase_summary_complete.loc['final_component_transportation']])
    phase3 = sum([phase_summary_complete.loc['passenger_transportation']])
    
    # Create new dataframe of final combined phase totals
    phase_summary_condensed = pd.DataFrame({phase1_label: phase1, phase2_label: phase2, phase3_label: phase3}).T
    
    # Order final output
    phase_summary_condensed = phase_summary_condensed.reindex([phase1_label, phase2_label, phase3_label])
    
    return phase_summary_condensed

def calculatePhaseImpacts(phase_summary_condensed, emissions_eq_conversion):
    '''Calculates total phase impacts based on phase summary and provided 
    conversion factors.
    
    Note that PM 2.5 is listed as 'PM25' to prevent machine misinterpretation.'''
    
    # Create new dataframe of CO2eq and SO2eq values by phase
    impact_values = phase_summary_condensed.copy()
    
    # Extract emissions info
    ## Initialize equivalent emissions lists
    CO2eq_list = {}
    SO2eq_list = {}
    PM25eq_list = {}

    ## Populate equivalent emissions lists
    for row in emissions_eq_conversion.index:

        ## Extract required data
        category = emissions_eq_conversion.loc[row]['category']
        emission = emissions_eq_conversion.loc[row]['emission']
        conversion = emissions_eq_conversion.loc[row]['conversion']

        ## Categorize data and update appropriate list
        if category == 'global_warming_potential':
            CO2eq_list.update({emission: conversion})
        elif category == 'air_acidification_potential':
            SO2eq_list.update({emission: conversion})
        elif category == 'particulate_matter_potential':
            PM25eq_list.update({emission: conversion})
        else:
            print("Entry {} was not found to be in the expected categories.".format(emission))
            
    # Calculate equivalent emissions for all emissions columns
    for emission in impact_values:
        conversion_factor = emissions_eq_conversion.loc[emissions_eq_conversion['emission'] == emission]['conversion'].values[0]
        impact_values[emission] = phase_summary_condensed[emission] * conversion_factor
    
    # Identify CO2eq, SO2eq, and PM25eq emissions
    CO2eqs = list(CO2eq_list.keys())
    SO2eqs = list(SO2eq_list.keys())
    PM25eqs = list(PM25eq_list.keys())
    
    # Sum all CO2 equivalent values in new total_impacts column
    impact_values['CO2_eq_kg'] = impact_values[CO2eqs].sum(axis = 1)
    
    # Sum all SO2 equivalent values in new total_impacts column
    impact_values['SO2_eq_kg'] = impact_values[SO2eqs].sum(axis = 1)
    
    # Sum all PM25 equivalent values in new total_impacts column
    impact_values['PM25_eq_kg'] = impact_values[PM25eqs].sum(axis = 1)
    
    # Create final total_impacts_phase dataframe containing only equivalent emissions
    total_impacts_phase = impact_values.drop(CO2eqs, axis = 1).drop(SO2eqs, axis = 1).drop(PM25eqs, axis = 1)
    
    return total_impacts_phase

def calculateLifetimeImpacts(total_impacts_phase, home_country):
    '''Combines impacts by phase to display lifetime impacts by category.'''
    
    # Add impacts across phases, saving in new dataframe and flagging home country for tracking across model runs
    total_impacts_lifetime = pd.DataFrame({'total_impacts_{}'.format(home_country): total_impacts_phase.sum(axis=0)}).T
    
    return total_impacts_lifetime