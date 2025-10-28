*** PASS-THROUGH REGRESSIONS ***

clear
file close _all
capture log close
set more off
set matsize 2000

use "$dirpath/stata_data/data_regressions_passthrough.dta", clear

xi i.month*i.year i.weekd i.hour i.month|temp i.month|tempx i.ym|windx i.month*i.hour i.ym*i.hour i.month|day ///
	i.peak i.peak|eprice i.peak|leprice i.ym|day i.yq|time i.yb|time
	

* BASELINE REGRESSIONS ---------------------------------------------------------
log using "$dirpath/tables/table_cost_pt_base.log", replace	

preserve 
drop if rd == 1

// specification
global demandcontrols = "temp tempx humid"
global supplycontrols = "windx windx2"
global controls = "coal gas brent"
global basefe = "_Ihour_* _Iyear* _Iweek* _Imonth_*"
global controls1 = "hour#(c.coal c.gas c.brent) coal gas brent"

global maincost = "ecost2"
global instruments = "eprice"

// pass-through estimation
*(2) - MONTH-HOUR FE
regress $maincost $instruments $supplycontrols $demandcontrols $controls $basefe _ImonXyea*, robust
estimates store spec_first1
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea*, robust first
estimates store spec1
estat firststage
mat ftest1 = r(singleresults)
	
*(3) - MONTHxTEMP
regress $maincost $instruments $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXtem*, robust
estimates store spec_first2
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXtem*, robust first
estimates store spec2
estat firststage
mat ftest2 = r(singleresults)

*(4) - MONTHxWIND
regress $maincost $instruments $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou*, robust
estimates store spec_first3
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou*, robust first
estimates store spec3
estat firststage
mat ftest3 = r(singleresults)

*(5) - HOURxINPUT
regress $maincost $instruments $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_first4
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust first
estimates store spec4
estat firststage
mat ftest4 = r(singleresults)

*(5) - HOURxINPUT
regress $maincost $instruments $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_first5
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust first
estimates store spec5
estat firststage
mat ftest5 = r(singleresults)

restore

log close


// WRITE TABLE --------
local N_spec = 5
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_base.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Cost Pass-through Regression Results} \label{tab:cost_pt}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " & \textbf{(`i')} "
}
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
	
file write myfile "Mg. Emissions Costs $(\rho)$ "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[$maincost]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[$maincost]) ")"
}
file write myfile " \\[\sep] \hline \\[-\sep]" _n

file write myfile "Temperature "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {		
		file write myfile " " %4.3f (_b[temp]) ""
	}
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {		
		file write myfile " (" %4.3f (_se[temp]) ")"
	}
}
file write myfile " \\[\sep] " _n
file write myfile "Maximum Temperature "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {		
		file write myfile " " %4.3f (_b[tempx]) ""
	}
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {		
		file write myfile " (" %4.3f (_se[tempx]) ")"
	}
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed Squared"
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx2]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx2]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Coal "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[coal]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[coal]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Gas "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[gas]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[gas]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Brent "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[brent]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[brent]) ")"
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile " F-test " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " &" 
	file write myfile " " %4.1f (ftest`i'[1,4]) " "
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"MonthXTemp,MaxTemp	& N & Y & N & Y & Y  \\" _n ///	
"MonthXHour FE		& N & N & Y & Y & Y  \\" _n ///	
"HourXInput			& N & N & N & N & Y  \\[\sep]" _n ///
// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"All specifications include month of sample, weekday, and hour fixed effects, as well as weather and demand controls " _n ///
"(temperature, maximum temperature, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil). The marginal emissions cost is instrumented with the emissions price. " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile

// WRITE TABLE --------
local N_spec = 5
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_first.tex", write replace	
file write myfile "\begin{table}[!ht]" _n ///
"\centering" _n ///
"\caption{First Stage for Marginal Emissions Costs} \label{tab:cost_pt_first}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " & \textbf{(`i')} "
}
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
	
file write myfile "Emissions Price "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[eprice]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[eprice]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Temperature "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &"
	if (`i'==1 | `i'== 3) {
		file write myfile " " %4.3f (_b[temp]) ""
	}
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {		
		file write myfile " (" %4.3f (_se[temp]) ")"
	}
}
file write myfile " \\[\sep] " _n
file write myfile "Maximum Temperature "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {		
		file write myfile " " %4.3f (_b[tempx]) ""
	}
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {
		file write myfile " (" %4.3f (_se[tempx]) ")"
	}
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed Squared"
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx2]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx2]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Coal "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[coal]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[coal]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Gas "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[gas]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[gas]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Brent "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[brent]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_first`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[brent]) ")"
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"MonthXTemp,MaxTemp	& N & Y & N & Y & Y  \\" _n ///	
"MonthXHour FE		& N & N & Y & Y & Y  \\" _n ///	
"HourXInput			& N & N & N & N & Y  \\[\sep]" _n ///
// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"All specifications include month of sample, weekday, and hour fixed effects, as well as weather and demand controls " _n ///
"(temperature, maximum temperature, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil). " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile


* ADDITIONAL SPECIFICATIONS ----------------------------------------------------
* Includes the most comprehensive specification in baseline results plus additional

log using "$dirpath/tables/table_cost_pt_additional.log", replace	

preserve 
drop if rd == 1

// specification
global demandcontrols = "temp tempx humid"
global supplycontrols = "windx windx2"
global controls = "coal gas brent"
global basefe = "_Ihour_* _Iyear* _Iweek* _Imonth_* _ImonXyea* _ImonXhou* _ImonXtem*"
global controls1 = "hour#(c.coal c.gas c.brent) coal gas brent"

global maincost = "ecost2"
global instruments = "eprice"

// pass-through estimation
*(1) - BASELINE
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe, robust first
estimates store spec_add1
estat firststage
mat ftest_add1 = r(singleresults)

*(2) - QUADRATIC INPUTS
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe coal2 gas2 brent2, robust first
estimates store spec_add2
estat firststage
mat ftest_add2 = r(singleresults)

*(3) - QUADRATIC TEMPERATURE
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe coal2 gas2 brent2 temp2, robust first
estimates store spec_add3
estat firststage
mat ftest_add3 = r(singleresults)

*(4) - BOTH
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe coal2 gas2 brent2 temp2 windtime, robust first
estimates store spec_add4
estat firststage
mat ftest_add4 = r(singleresults)

restore

log close


// WRITE TABLE --------
local N_spec = 4
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_additional.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Cost Pass-through Regression - Additional controls} \label{tab:cost_pt_additional}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " & \textbf{(`i')} "
}
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
	
file write myfile "Mg. Emissions Costs $(\rho)$ "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[$maincost]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[$maincost]) ")"
}
file write myfile " \\[\sep] \hline \\[-\sep]" _n
file write myfile "Wind Speed "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed Squared"
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx2]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx2]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed X Trend "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	if (`i' > 3) {
		file write myfile " " %4.3f (_b[windtime]) ""
	}
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_add`i'
	file write myfile " &" 
	if (`i' > 3) {
		file write myfile " (" %4.3f (_se[windtime]) ")"
	}
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile " F-test " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " &" 
	file write myfile " " %4.1f (ftest_add`i'[1,4]) " "
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"Quadratic Inputs	& N & Y & Y & Y  \\" _n ///	
"Temperature Squared	& N & N & Y & Y  \\" _n ///
"Wind Speed Trend	& N & N & Y & Y  \\[\sep]" _n ///		
// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"All specifications include month of sample, weekday, and hour fixed effects, as well as weather and demand controls " _n ///
"(temperature, maximum temperature, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil). The marginal emissions cost is instrumented with the emissions price. " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile


* INTERPOLATED REGRESSIONS -----------------------------------------------------

log using "$dirpath/tables/table_cost_pt_interpolated.log", replace	

preserve 
drop if rd == 1

// specification
global demandcontrols = "temp tempx humid"
global supplycontrols = "windx windx2"
global controls = "coal gas brent"
global basefe = "_Ihour_* _Iyear* _Iweek* _Imonth_*"
global controls1 = "hour#(c.coal c.gas c.brent) coal gas brent"
global instruments = "eprice"


global maincost = "ecost_int"
*(2) - MONTH-HOUR FE
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea*, robust
estimates store spec_int1
	
*(3) - MONTHxTEMP
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXtem*, robust
estimates store spec_int2
	
*(4) - MONTHxWIND
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou*, robust
estimates store spec_int3

*(5) - HOURxINPUT
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_int4

*(5) - HOURxINPUT
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_int5

global maincost = "ecost"
*(2) - MONTH-HOUR FE
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea*, robust
estimates store spec_exact1
	
*(3) - MONTHxTEMP
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXtem*, robust
estimates store spec_exact2
	
*(4) - MONTHxWIND
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXhou* _ImonXtem*, robust
estimates store spec_exact3

*(5) - HOURxINPUT
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_exact4

*(5) - HOURxINPUT
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_exact5

restore

log close


// WRITE TABLE --------
local N_spec = 5
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_interpolated.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Cost Pass-through Regression Results for different Emissions Assumptions} " ///
"\label{tab:cost_pt_interpolated}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " & \textbf{(`i')} "
}
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
file write myfile "Interpolated Emissions Costs "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_int`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost_int]) ""
}
file write myfile " \\ " _n
file write myfile "\qquad Obs. = "  %7.0fc (e(N)) " " 
forvalues i = 1(1)`N_spec' {
	estimates restore spec_int`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost_int]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Mg. Emissions Costs \\ (Units \& Technologies) "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost2]) ""
}
file write myfile " \\ " _n
file write myfile "\qquad Obs. = "  %7.0fc (e(N)) " " 
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost2]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Mg. Emissions Costs \\ (Units Only) "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_exact`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost]) ""
}
file write myfile " \\ " _n
file write myfile "\qquad Obs. = "  %7.0fc (e(N)) " " 
forvalues i = 1(1)`N_spec' {
	estimates restore spec_exact`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost]) ")"
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"MonthXTemp,MaxTemp	& N & Y & N & Y & Y  \\" _n ///	
"MonthXHour FE		& N & N & Y & Y & Y  \\" _n ///	
"HourXInput			& N & N & N & N & Y  \\[\sep]" _n ///
// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"All specifications include month of sample, weekday, and hour fixed effects, as well as weather and demand controls " _n ///
"(temperature, maximum temperature, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil). The marginal emissions cost is instrumented with the emissions price. " _n ///
"Robust standard errors in parentheses.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile


* RD INCLUDED ------------------------------------------------------------------
log using "$dirpath/tables/table_cost_pt_rd.log", replace	

// specification
global demandcontrols = "temp tempx humid"
global supplycontrols = "windx windx2"
global controls = "coal gas brent"
global basefe = "_Ihour_* _Iyear* _Iweek* _Imonth_*"
global controls1 = "hour#(c.coal c.gas c.brent) coal gas brent"

global maincost = "ecost2"
global instruments = "eprice"

// pass-through estimation
*(2) - MONTH-HOUR FE
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea*, robust first
estimates store spec_rd1
estat firststage
mat ftest_rd1 = r(singleresults)

*(3) - MONTHxTEMP
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXtem*, robust first
estimates store spec_rd2
estat firststage
mat ftest_rd2 = r(singleresults)
	
*(4) - MONTHxWIND
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou*, robust first
estimates store spec_rd3
estat firststage
mat ftest_rd3 = r(singleresults)

*(4) - MONTHxWIND
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust first
estimates store spec_rd4
estat firststage
mat ftest_rd4 = r(singleresults)

*(5) - HOURxINPUT
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust first
estimates store spec_rd5
estat firststage
mat ftest_rd5 = r(singleresults)

log close


// WRITE TABLE --------
local N_spec = 5
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_rd.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Cost Pass-through Regression Results - Royal Decree Included} \label{tab:cost_pt_rd}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " & \textbf{(`i')} "
}
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
	
file write myfile "Mg. Emissions Costs $(\rho)$ "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[$maincost]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[$maincost]) ")"
}
file write myfile " \\[\sep] \hline \\[-\sep]" _n

file write myfile "Temperature "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {	
		file write myfile " " %4.3f (_b[temp]) ""
	}
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {
		file write myfile " (" %4.3f (_se[temp]) ")"
	}
}
file write myfile " \\[\sep] " _n
file write myfile "Maximum Temperature "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {	
		file write myfile " " %4.3f (_b[tempx]) ""
	}
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	if (`i'==1 | `i'== 3) {	
		file write myfile " (" %4.3f (_se[tempx]) ")"
	}
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Wind Speed Squared"
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[windx2]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[windx2]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Coal "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[coal]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[coal]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Gas "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[gas]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[gas]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Brent "
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[brent]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec_1' {
	estimates restore spec_rd`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[brent]) ")"
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile " F-test " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " &" 
	file write myfile " " %4.1f (ftest_rd`i'[1,4]) " "
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"MonthXTemp,MaxTemp	& N & Y & N & Y & Y  \\" _n ///	
"MonthXHour FE		& N & N & Y & Y & Y  \\" _n ///	
"HourXInput			& N & N & N & N & Y  \\[\sep]" _n ///
		
// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to June 2007, includes all thermal units in the Spanish electricity market. " _n ///
"All specifications include month of sample, weekday, and hour fixed effects, as well as weather and demand controls " _n ///
"(temperature, maximum temperature, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil). The marginal emissions cost is instrumented with the emissions price. " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile


* PEAK/OFF-PEAK REGRESSIONS ----------------------------------------------------
log using "$dirpath/tables/table_cost_pt_peak.log", replace

// specification
global demandcontrols = "temp tempx humid"
global supplycontrols = "windx windx2"
global controls = "coal gas brent"
global basefe = "_Ihour_* _Iyear* _Iweek* _Imonth_*"
global controls1 = "hour#(c.coal c.gas c.brent) coal gas brent"

global maincost = "ecost2_peak ecost2_off"
global instruments = "eprice _IpeaXepric_1"

preserve 
drop if rd == 1

// pass-through estimation
*(2) - MONTH-HOUR FE
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea*, robust
estimates store spec_peak1

*(3) - MONTHxTEMP
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXtem*, robust
estimates store spec_peak2

*(4) - MONTHxWIND
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou*, robust
estimates store spec_peak3

*(5) - HOURxINPUT
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_peak4

*(5) - HOURxINPUT
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols $controls1 $basefe _ImonXyea* _ImonXhou* _ImonXtem*, robust
estimates store spec_peak5

restore


log close


// WRITE TABLE --------
local N_spec = 5
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_peak.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Cost Pass-through Regression Results: Peak vs. Non-Peak} \label{tab:cost_pt_peak}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " & \textbf{(`i')} "
}
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
	
file write myfile "Mg. Emissions Costs - Peak "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peak`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost2_peak]) ""
}
file write myfile " \\ " _n 
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peak`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost2_peak]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Mg. Emissions Costs - Off Peak "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peak`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost2_off]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peak`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost2_off]) ")"
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"MonthXTemp,MaxTemp	& N & Y & N & Y & Y  \\" _n ///	
"MonthXHour FE		& N & N & Y & Y & Y  \\" _n ///	
"HourXInput			& N & N & N & N & Y  \\[\sep]" _n ///
// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"Only peak hours are included (between 8am and 8pm). " _n ///
"All specifications include month of sample, weekday, and hour fixed effects, as well as weather and demand controls " _n ///
"(temperature, maximum temperature, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil). The marginal emissions cost is instrumented with the emissions price. " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile


* TOTAL vs EMISSIONS COST ------------------------------------------------------
global demandcontrols = "temp tempx humid"
global supplycontrols = "windx windx2"
global controls1 = "hour#(c.coal c.gas c.brent) coal gas brent"
global controls1_log = "hour#(c.lcoal c.lgas c.lbrent) lcoal lgas lbrent"
global basefe = "year##month i.weekd month##hour"

global instruments = " eprice _IpeaXepr "
global instruments_log = " leprice _IpeaXlepr "

drop if rd == 1

ivregress 2sls mg_price (ecost2_peak ecost2_off = $instruments) ///
			$supplycontrols $demandcontrols $controls1 ///
			$basefe if totalcost2 != ., robust
estimates store spec_peaka1

ivregress 2sls lmg_price (lecost2_peak lecost2_off = $instruments_log) ///
			$supplycontrols $demandcontrols $controls1_log ///
			$basefe if totalcost2 != ., robust
estimates store spec_peaka2
							
ivregress 2sls mg_price (totalcost2_peak totalcost2_off = $instruments) ///
			$supplycontrols $demandcontrols $controls1 ///
			$basefe if totalcost2 != ., robust
estimates store spec_peaka3
				
ivregress 2sls lmg_price (ltotalcost2_peak ltotalcost2_off = $instruments_log) ///
			$supplycontrols $demandcontrols $controls1_log ///
			$basefe if totalcost2 != ., robust
estimates store spec_peaka4
			
// WRITE TABLE --------
local N_spec = 4
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_peak_alternatives.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Emissions vs. Non Emissions Costs: Peak vs. Off-Peak} \label{tab:cost_pt_peak_alternatives}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
file write myfile " & \multicolumn{2}{c}{\textbf{Emissions Costs}}  &  \multicolumn{2}{c}{\textbf{Total Mg. Costs}} \\ "
file write myfile " & Linear & Logs & Linear & Logs "
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
	
file write myfile "Peak Pass-Through "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peaka`i'
	file write myfile " &" 
	capture file write myfile " " %4.3f (_b[ecost2_peak]) ""
	capture file write myfile " " %4.3f (_b[lecost2_peak]) ""
	capture file write myfile " " %4.3f (_b[totalcost2_peak]) ""
	capture file write myfile " " %4.3f (_b[ltotalcost2_peak]) ""
}
file write myfile " \\ " _n 
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peaka`i'
	file write myfile " & (" 
	capture file write myfile "" %4.3f (_se[ecost2_peak]) ""
	capture file write myfile "" %4.3f (_se[lecost2_peak]) ""
	capture file write myfile "" %4.3f (_se[totalcost2_peak]) ""
	capture file write myfile "" %4.3f (_se[ltotalcost2_peak]) ""
	file write myfile ")" 
}
file write myfile " \\[\sep] " _n
file write myfile "Off-Peak Pass-Through "
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peaka`i'
	file write myfile " &" 
	capture file write myfile "" %4.3f (_b[ecost2_off]) ""
	capture file write myfile "" %4.3f (_b[lecost2_off]) ""
	capture file write myfile "" %4.3f (_b[totalcost2_off]) ""
	capture file write myfile "" %4.3f (_b[ltotalcost2_off]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec_peaka`i'
	file write myfile " & (" 
	capture file write myfile "" %4.3f (_se[ecost2_off]) ""
	capture file write myfile "" %4.3f (_se[lecost2_off]) ""
	capture file write myfile "" %4.3f (_se[totalcost2_off]) ""
	capture file write myfile "" %4.3f (_se[ltotalcost2_off]) ""
	file write myfile ")" 
}
// revise specifications and description so that it reflects regressions
file write myfile "\\ \hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"Only peak hours are included (between 8am and 8pm). " _n ///
"All specifications include month of sample, weekday, and month-hour fixed effects, as well as weather and demand controls " _n ///
"(temperature, maximum temperature, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and hourly linear (logarithmic) controls for commodity prices of " _n ///
"coal, gas, and oil). " _n ///
" (Log of) Costs are instrumented with (the log of) the emissions price. " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile
