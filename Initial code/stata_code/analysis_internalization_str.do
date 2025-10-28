*** STRUCTURAL INTERNALIZATION ***
clear
capture log close
file close _all
set matsize 800
set more off

use "$dirpath/stata_data/data_regressions_structural.dta", clear	

// MAIN TABLE ------------------------------------------------------------------
log using "$dirpath/tables/table_internalization.log", replace

global instruments = "temp windx humid temperatura"

// Basic
xi: ivreg pricehat mg_cost cost_CO2, nocons cluster(id) noomitted
estimates store spec1

// Unit FE		
xi: ivreg pricehat mg_cost cost_CO2 i.up, cluster(id) noomitted
estimates store spec2
		
// Seasonality controls
xi: ivreg pricehat mg_cost cost_CO2 summer* spring* winter* weekdays i.up, cluster(id) noomitted
estimates store spec3

// Instrumented markup estimate
xi: ivreg price mg_cost cost_CO2 (markup = $instruments) summer* spring* winter* weekdays i.up, cluster(id)  
estimates store spec4
	
				
forvalues f=1(1)4 {

		// Basic
		xi: ivreg pricehat mg_cost cost_CO2 if firm_code == `f', nocons cluster(id) noomitted
		estimates store spec1_`f'
		
		// Unit FE
		xi: ivreg pricehat mg_cost cost_CO2 i.up if firm_code == `f', cluster(id) noomitted
		estimates store spec2_`f'
		
		// Seasonality controls
		xi: ivreg pricehat mg_cost cost_CO2 summer* spring* winter* weekdays i.up if firm_code == `f', cluster(id) noomitted
		estimates store spec3_`f'

		// Instrumented markup estimate
		xi: ivreg price mg_cost cost_CO2 (markup = $instruments) summer* spring* winter* weekdays i.up if firm_code == `f', cluster(id) noomitted 
		estimates store spec4_`f'

}
	

log close

	
// WRITE TABLE
local N_spec = 4
local specNames = "No_FE Unit_FE Unit_FE_+_Season Spec.3_+_Markup_(IV)"

file open myfile1 using "$dirpath/tables/table_internalization.tex", write replace
file write myfile1 "\begin{table}" _n ///
"\centering" _n ///
"\caption{Test based on structural equations} \label{tab:intern_structural}" _n _n
file write myfile1 "\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)5 {
	file write myfile1 " c "
}
file write myfile1 "}" _n ///
"\\ \hline\hline " _n
file write myfile1 " & \textbf{All} "
forvalues i = 1(1)4 {
	file write myfile1 " & \textbf{Firm `i'} "
}
file write myfile1  "\\ \cline{2-6} \\[-\sep]" _n
file write myfile1 "\textbf{Emissions cost} ($\gamma$) \\[\sep]" _n
forvalues s = 1(1)`N_spec' {
	local name = subinstr(word("`specNames'",`s'),"_"," ",.) 
	file write myfile1 "(`s') `name'"
	estimates restore spec`s'
	file write myfile1 " & " %4.3f (_b[cost_CO2])
	forvalues i=1(1)4 {
		estimates restore spec`s'_`i'
		file write myfile1 " & " %4.3f (_b[cost_CO2])
	}
	file write myfile1 " \\ " _n
	estimates restore spec`s'
	file write myfile1 " & (" %4.3f (_se[cost_CO2]) ")"		
	forvalues i=1(1)4 {
		estimates restore spec`s'_`i'
		file write myfile1 " & (" %4.3f (_se[cost_CO2]) ")"
	}
	file write myfile1 "\\[\sep]" _n
}
file write myfile1 " \hline \\[-\sep]" _n	
file write myfile1 "\textbf{Input cost} ($\beta$) \\[\sep]" _n
forvalues s = 1(1)`N_spec' {
	local name = subinstr(word("`specNames'",`s'),"_"," ",.) 
	file write myfile1 "(`s') `name'"
	estimates restore spec`s'
	file write myfile1 " & " %4.3f (_b[mg_cost])
	forvalues i=1(1)4 {
		estimates restore spec`s'_`i'
		file write myfile1 " & " %4.3f (_b[mg_cost])
	}
	file write myfile1 " \\ " _n
	estimates restore spec`s'
	file write myfile1 " & (" %4.3f (_se[mg_cost]) ")"		
	forvalues i=1(1)4 {
		estimates restore spec`s'_`i'
		file write myfile1 " & (" %4.3f (_se[mg_cost]) ")"
	}
	file write myfile1 "\\[\sep]" _n
}
file write myfile1 " \hline \\[-\sep]" _n
file write myfile1 "\textbf{Markup} ($\theta$) \\[\sep]" _n
forvalues s = `N_spec'(1)`N_spec' {
	local name = subinstr(word("`specNames'",`s'),"_"," ",.) 
	file write myfile1 "(`s') `name'"
	estimates restore spec`s'
	file write myfile1 " & " %4.3f (_b[markup])
	forvalues i=1(1)4 {
		estimates restore spec`s'_`i'
		file write myfile1 " & " %4.3f (_b[markup])
	}
	file write myfile1 " \\ " _n
	estimates restore spec`s'
	file write myfile1 " & (" %4.3f (_se[markup]) ")"		
	forvalues i=1(1)4 {
		estimates restore spec`s'_`i'
		file write myfile1 " & (" %4.3f (_se[markup]) ")"
	}
	file write myfile1 "\\[\sep]" _n
}
file write myfile1 " \hline \\[-\sep]" _n			
// Obs
file write myfile1 "Obs."
estimates restore spec1
file write myfile1 " & " %12.0fc (e(N))	
forvalues i = 1(1)4 {
	estimates restore spec1_`i'
	file write myfile1 " & " %12.0fc (e(N))
}
file write myfile1 " \\[\sep] \hline \hline  \vspace{-18pt}" _n
file write myfile1 "\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize \vspace{6pt}" _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"Standard errors clustered at the unit level.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile1
	

// STANDARD ERRORS -------------------------------------------------------------

log using "$dirpath/tables/table_internalization_stderrors.log", replace


global instruments = "temp windx humid temperatura"

// Unit 
xi: ivreg pricehat mg_cost cost_CO2 i.up, cluster(id) noomitted
estimates store spec_sd1
		
// Robust
xi: ivreg pricehat mg_cost cost_CO2 i.up, robust noomitted
estimates store spec_sd2

// Firm-Week
xi: ivreg pricehat mg_cost cost_CO2 i.up, cluster(firmday) noomitted
estimates store spec_sd3

// Firm-Month of Sample
xi: ivreg pricehat mg_cost cost_CO2 i.up, cluster(firmym) noomitted
estimates store spec_sd4
				
forvalues f=1(1)4 {

		// 
		xi: ivreg pricehat mg_cost cost_CO2 i.up if firm_code == `f', cluster(id) noomitted
		estimates store spec_sd1_`f'
		
		// 
		xi: ivreg pricehat mg_cost cost_CO2 i.up if firm_code == `f', robust noomitted
		estimates store spec_sd2_`f'

		// 
		xi: ivreg pricehat mg_cost cost_CO2 i.up if firm_code == `f', cluster(firmday) noomitted
		estimates store spec_sd3_`f'
		
		// 
		xi: ivreg pricehat mg_cost cost_CO2 i.up if firm_code == `f', cluster(firmym) noomitted
		estimates store spec_sd4_`f'

}
	

log close

	
// WRITE TABLE
local N_spec = 4
local specNames = "Unit-Level_Clusters Robust_Std._Errors Firm-Day_Clusters Firm-Month_Clusters"

capture file close myfile1
file open myfile1 using "$dirpath/tables/table_internalization_stderrors.tex", write replace
file write myfile1 "\begin{table}" _n ///
"\centering" _n ///
"\caption{Test based on structural equations -- Effects of Clustering} \label{tab:intern_structural_stderrors}" _n _n
file write myfile1 "\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)5 {
	file write myfile1 " c "
}
file write myfile1 "}" _n ///
"\hline\hline " _n
file write myfile1 " & \textbf{All} "
forvalues i = 1(1)4 {
	file write myfile1 " & \textbf{Firm `i'} "
}
file write myfile1  "\\ \cline{2-6} \\[-\sep]" _n
file write myfile1 "\textbf{Emissions cost} ($\gamma$) " _n
estimates restore spec_sd1
file write myfile1 " & " %4.3f (_b[cost_CO2])
forvalues i=1(1)4 {
	estimates restore spec_sd1_`i'
	file write myfile1 " & " %4.3f (_b[cost_CO2])
}
file write myfile1 " \\[\sep] " _n
forvalues s = 1(1)`N_spec' {
	local name = subinstr(word("`specNames'",`s'),"_"," ",.) 
	file write myfile1 "(`s') `name'"
	estimates restore spec_sd`s'
	file write myfile1 " & (" %4.3f (_se[cost_CO2]) ")"		
	forvalues i=1(1)4 {
		estimates restore spec_sd`s'_`i'
		file write myfile1 " & (" %4.3f (_se[cost_CO2]) ")"
	}
	file write myfile1 "\\[\sep]" _n
}
file write myfile1 " \hline \\[-\sep]" _n	
file write myfile1 "\textbf{Input cost} ($\beta$) " _n
estimates restore spec_sd1
file write myfile1 " & " %4.3f (_b[mg_cost])
forvalues i=1(1)4 {
	estimates restore spec_sd1_`i'
	file write myfile1 " & " %4.3f (_b[mg_cost])
}
file write myfile1 " \\[\sep] " _n
forvalues s = 1(1)`N_spec' {
	local name = subinstr(word("`specNames'",`s'),"_"," ",.) 
	file write myfile1 "(`s') `name'"
	estimates restore spec_sd`s'
	file write myfile1 " & (" %4.3f (_se[mg_cost]) ")"		
	forvalues i=1(1)4 {
		estimates restore spec_sd`s'_`i'
		file write myfile1 " & (" %4.3f (_se[mg_cost]) ")"
	}
	file write myfile1 "\\[\sep]" _n
}
file write myfile1 " \hline \\[-\sep]" _n			
// Obs
file write myfile1 "Obs."
estimates restore spec_sd1
file write myfile1 " & " %12.0fc (e(N))	
forvalues i = 1(1)4 {
	estimates restore spec_sd1_`i'
	file write myfile1 " & " %12.0fc (e(N))
}
file write myfile1 " \\[\sep] \hline \hline  \vspace{-18pt}" _n
file write myfile1 "\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize \vspace{6pt}" _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"Regression includes unit fixed effects. Each row considers a different level of clustering: " _n ///
"unit-level clusters (our baseline specification), robsut White standard errors, firm-day clusters to " _n ///
"account for correlation in bidding within a firm at a given day, and firm-month of sample clusters to " _n ///
"account for longer temporal clustering. }" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile1
