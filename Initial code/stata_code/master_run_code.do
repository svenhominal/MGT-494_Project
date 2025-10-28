*********************************************************************************
*	CODE FOR GETTING RESULTS IN PAPER 		    				   	       		*
*	"Pass-through of emissions costs in electricity markets"			       	*
*		by Natalia Fabra and Mar Reguant										*
* 																				*
* Last edited: March 2014														*
* Questions? mreguant@stanford.edu												*
*********************************************************************************

clear all
set type double
set more off
program drop _all

//directory with raw data and project (set to own local folder)
global datapath = "/Volumes/Dades/Dropbox/DATA"
global dirpath  = "/Volumes/Dades/Dropbox/PROJECTS/internalization2/submission/FINAL SUBMISSION/20130186_data"


* 1) DATA CLEAN-UP / PRELIMINARIES *********************************************
// commented out (needs raw data)
*qui do $dirpath/stata_code/data_create
*qui do $dirpath/stata_code/data_create_demand
*qui do $dirpath/stata_code/data_merge
*qui do $dirpath/stata_code/data_create_matlab

* matlab elasticityMarkupAnalysis.m 	// Note: To be run in Matlab
										// Requires matlab raw files, sample included.
										// Matlab code requires cplex solver (see readme).


* 2) SUMMARY FIGURES ***********************************************************
do "$dirpath/stata_code/prelim_graphs"


* 3) MAIN ANALYSIS *************************************************************
do "$dirpath/stata_code/analysis_passthrough_rf"
do "$dirpath/stata_code/analysis_internalization_str"
do "$dirpath/stata_code/analysis_markups"		// (on subsample)
do "$dirpath/stata_code/analysis_rigidities" 	// (on subsample)


* 4) ADDITONAL MATERIAL ********************************************************
do $dirpath/stata_code/analysis_passthrough_rf_robustness
