#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

hsrlca.model: High-speed rail life cycle assessment model object
==========================================================

hsrlca.model provides the class object for high-speed rail life cycle 
assessment model trials, designed for research on Chinese rail development 
in continental Southeast Asia. It handles data across various model scenarios,
using functions from the module hsrlca_calc to execute model calculations. All
data transformations are saved within the object, enabling later access and 
compilation across scenarios and trials.
   
Dependencies
------------
numpy
pandas
hsrlca.calc

Input Requirements for Full Model Execution
--------------
Data file names:
    data_dir : str
    up_inputs_base : str
    up_emissions_base : str
    national_energy_supply : str
    unit_energy_emissions : str
    emissions_eq_conversion : str
    trade_distances : str
    rail_allocation : str

Normalization parameters:
    avg_train_capacity : int
    avg_train_capacity_filled : float
    avg_daily_trips_per_train : int
    avg_train_trip_distance : float
    avg_train_lifespan : float
    avg_number_active_trains : int
    avg_train_mass : float
    avg_infrastructure_lifespan : float
    avg_pct_ballasted_track : float
    days : float

Model Execution Procedure
-------------------------
The following steps, in order, will execute a full trial run of the model, 
given appropriate data inputs. The module hsrlca is imported as lca.

    1. CTR_scenario = lca.Scenario('CountryName')
            where CTR is the country code and scenario is a unique indicator;
            optional parameter "verbose" defaults to False
            
    2. CTR_scenario.set_data(data_dir,
                            up_inputs_base,
                            up_emissions_base,
                            national_energy_supply,
                            unit_energy_emissions,
                            emissions_eq_conversion,
                            trade_distances,
                            rail_allocation)
                            
    3. CTR_scenario.set_scenario(up_countries_CTR_scenario)
            using a scenario-specific data file
            
    4. CTR_scenario.set_norm_params(avg_train_capacity,
                            avg_train_capacity_filled,
                            avg_daily_trips_per_train,
                            avg_train_trip_distance,
                            avg_train_lifespan,
                            avg_number_active_trains,
                            avg_train_mass,
                            avg_infrastructure_lifespan,
                            avg_pct_ballasted_track,
                            days)
                            
    5. CTR_scenario.make_trade_schedule()
    
    6. CTR_scenario.make_transport_schedule()
    
    7. CTR_scenario.update_inputs_transportation()
    
    8. CTR_scenario.get_energy_mix()
    
    9. CTR_scenario.get_energy_mix_emissions()
    
    10. CTR_scenario.update_emissions()
    
    11. CTR_scenario.update_inputs_electricity()
    
    12. CTR_scenario.update_inputs_passengers()
    
    13. CTR_scenario.make_emissions_schedule()
    
    14. CTR_scenario.get_total_requirements()
    
    15. CTR_scenario.get_total_emissions()
    
    16. CTR_scenario.get_phase_results()
    
    17. CTR_scenario.get_condensed_results()
    
    18. CTR_scenario.get_total_phase_impacts()
    
    19. CTR_scenario.get_total_lifetime_impacts()

'''

import numpy as np
import pandas as pd
import hsrlca.calc as calc

class Scenario:
    '''Creates independent scenarios of the life cycle assessment model, 
    allowing execution of differentiated trials using separate data sets 
    within a single modeling script'''
    
    
    # Initialization    
    def __init__(self, home_country, verbose = False):
        self.home_country = home_country
        self.verbose = verbose
        
    
    # Data Inputs and Parameter Definition
    
    def set_data(self,
                 data_dir,
                 up_inputs_base,
                 up_emissions_base,
                 national_energy_supply,
                 unit_energy_emissions,
                 emissions_eq_conversion,
                 trade_distances,
                 rail_allocation):
        self.data_dir = data_dir
        self.up_inputs_base = pd.read_csv(data_dir + '/' + up_inputs_base)
        self.up_emissions_base = pd.read_csv(data_dir + '/' + up_emissions_base)
        self.national_energy_supply = pd.read_csv(data_dir + '/' + national_energy_supply)
        self.unit_energy_emissions = pd.read_csv(data_dir + '/' + unit_energy_emissions)
        self.emissions_eq_conversion = pd.read_csv(data_dir + '/' + emissions_eq_conversion)
        self.trade_distances = pd.read_csv(data_dir + '/' + trade_distances)
        self.rail_allocation = rail_allocation
    
    def set_scenario(self, up_countries):
        self.up_countries = pd.read_csv(self.data_dir + '/' + up_countries)
    
    def set_norm_params(self,
                        avg_train_capacity,
                        avg_train_capacity_filled,
                        avg_daily_trips_per_train,
                        avg_train_trip_distance,
                        avg_train_lifespan,
                        avg_number_active_trains,
                        avg_train_mass,
                        avg_infrastructure_lifespan,
                        avg_pct_ballasted_track,
                        days):
        self.norm_params = {'atc': avg_train_capacity,
                            'atcf': avg_train_capacity_filled,
                            'adt': avg_daily_trips_per_train,
                            'attd': avg_train_trip_distance,
                            'atl': avg_train_lifespan,
                            'anat': avg_number_active_trains,
                            'atm': avg_train_mass,
                            'ail': avg_infrastructure_lifespan,
                            'apbt': avg_pct_ballasted_track,
                            'apnt': np.round(1. - avg_pct_ballasted_track, 15), # Handles floating point arithmetic, allowing for non-restrictive 15 decimal points
                            'days': days
                           }
    
        
    # Trade and Transportation
    
    def make_trade_schedule(self):
        '''Construct trade_schedule, i.e. list of trades involved in product 
        lifecycle'''
        self.trade_schedule = calc.tradeSchedule(self.home_country, self.up_countries, self.up_inputs_base)
        if self.verbose == True:
            print("Trade schedule created as trade_schedule")
    
    def make_transport_schedule(self):
        '''Calculate transport_schedule, i.e. the distances entailed in each 
        trade sequence'''
        self.transport_schedule = calc.transportSchedule(self.trade_schedule, self.trade_distances, self.up_inputs_base)
        if self.verbose == True:
            print("Transport schedule created as transport_schedule")
    
    def update_inputs_transportation(self):
        '''Update the up_inputs_base dataset with transport requirements'''
        self.up_inputs_transport_update = calc.transportUpdate(self.transport_schedule, self.up_inputs_base, self.rail_allocation)
        if self.verbose == True:
            print("Updated unit process inputs table (input transportation) created as up_inputs_transport_update")
    
    
    # Energy Mixes
    
    def get_energy_mix(self):
        '''Create percentage energy_mix data set from raw values'''
        self.national_energy_mixes = calc.energyMixes(self.national_energy_supply)
        if self.verbose == True:
            print("National energy mixes table created as national_energy_mixes")
    
    def get_energy_mix_emissions(self):
        '''Calculate unit energy emissions based on percentage energy_mix data'''
        self.energy_mix_emissions = calc.energyMixEmissions(self.national_energy_mixes, self.unit_energy_emissions)
        if self.verbose == True:
            print("Unit energy mix emissions table created as energy_mix_emissions")
    
    def update_emissions(self):
        '''Update the up_emissions_base dataset with national unit energy 
        emissions'''
        self.up_emissions_complete = calc.energyMixEmissionsUpdate(self.up_emissions_base, self.energy_mix_emissions)
        if self.verbose == True:
            print("Updated unit process emissions table created as up_emissions_complete")
    
    def update_inputs_electricity(self):
        '''Update the up_inputs_transport_update dataset with the source of 
        electricity required for each unit process as dictated by the trade 
        scenario'''
        self.up_inputs_elec_update = calc.electricitySourceUpdate(self.up_inputs_transport_update, self.trade_schedule)
        if self.verbose == True:
            print("Updated unit process inputs table (electricity data) created as up_inputs_elec_update")
    
    
    # Passenger Transportation
    
    def update_inputs_passengers(self):
        '''Calculate passenger transportation requirements, which are tied to 
        one functional unit (1 p*km), given the input assumptions; update the 
        up_inputs_elec_update dataset with the passenger transportation 
        requirements indicated. The up_inputs_complete dataframe displays the 
        requirements for ONE UNIT (of given units); only passenger 
        transportation is in terms of the functional unit at this stage'''
        self.up_inputs_complete = calc.passengerUpdate(self.up_inputs_elec_update, **self.norm_params)
        if self.verbose == True:
            print("Updated unit process inputs table (passenger transportation) created as up_inputs_complete")
        
    
    # Emissions Schedule
    
    def make_emissions_schedule(self):
        '''Calculate the total emissions associated with the production of one
        unit of output per unit process, sorted by phase, based on national 
        energy mix calculations'''
        self.emissions_schedule = calc.calculateEmissionsSchedule(self.up_inputs_complete, self.up_emissions_complete)
        if self.verbose == True:
            print("Emissions schedule created as emissions_schedule")
        
    
    # Total Requirements
    
    def get_total_requirements(self):
        '''Calculate total materials required to produce one unit of train 
        operations, i.e. relate all elements of model to the functional unit'''
        self.up_total_requirements = calc.totalRequirements(self.up_inputs_complete)
        if self.verbose == True:
            print("Total unit process requirements table created as up_total_requirements")
        
    
    # Total Emissions
    
    def get_total_emissions(self):
        '''Calculate the total emissions associated with each unit process, 
        sorted by phase; rows show emissions for total required outputs'''
        self.emissions_total = calc.calculateEmissionsTotal(self.up_total_requirements, self.emissions_schedule)
        if self.verbose == True:
            print("Disaggregated total emissions table created as emissions_total")
    
        
    # Emissions Grouping
    
    def get_phase_results(self):
        '''Group total emissions by (disaggregated) subphase'''
        self.phase_summary_complete = calc.sumPhases(self.emissions_total)
        if self.verbose == True:
            print("Emissions table aggregated by subphase created as phase_summary_complete")
    
    def get_condensed_results(self):
        '''Condense results into three lifetime phases: raw material 
        extraction, construction, and operation'''
        self.phase_summary_condensed = calc.condensePhaseSums(self.phase_summary_complete, self.home_country)
        if self.verbose == True:
            print("Emissions table aggregated by phase created as phase_summary_condensed")
        
    
    # Impact Assessment
    
    def get_total_phase_impacts(self):
        '''Convert all emissions into CO2eq and SO2eq, presenting impacts on 
        global warming potential and air acidification potential, respectively'''
        self.total_impacts_phase = calc.calculatePhaseImpacts(self.phase_summary_condensed, self.emissions_eq_conversion)
        if self.verbose == True:
            print("Total impacts table aggregated by phase created as total_impacts_phase")
    
    def get_total_lifetime_impacts(self):
        '''Report lifetime emissions by impact category for the present model
        iteration'''
        self.total_impacts_lifetime = calc.calculateLifetimeImpacts(self.total_impacts_phase, self.home_country)
        if self.verbose == True:
            print("Total lifetime impacts table created as total_impacts_lifetime")