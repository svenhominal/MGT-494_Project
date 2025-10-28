*** PASS-THROUGH REGRESSIONS ***
clear
clear matrix
clear mata
program drop _all
file close _all
capture log close
set more off
set matsize 2000


* GRAPHS OF EPRICES-TIME -------------------------------------------------------
use "$dirpath/stata_data/data_regressions_passthrough.dta", clear

* indices
sort year month day
by year month day: keep if _n == 1
sort yb month day
by yb: gen indyb = _n
sort yq month day
by yq: gen indyq = _n
xi i.ym|day i.yb|indyb i.yq|indyq

* names
gen ym_name = string(year) +"-"+ string(month,"%02.0f")
gen yb_name = string(year) +"-"+ string(bimonth,"%02.0f")
gen yq_name = string(year) + "-Q" + string(quarter)

* graphs
qui reg eprice _Iym_* _IymXd*
predict lfit1
gen error1 = lfit1 - eprice

twoway (scatter eprice day) (line lfit1 day) if year > 2004, ///
	by(ym_name, row(1) compact note("")) xlabel(none) xtitle("")
graph export "$dirpath/figures/eprice_lfit1_time_all.pdf", as(pdf) replace

drop if rd == 1

twoway (scatter eprice day) (line lfit1 day) if year > 2004, ///
	by(ym_name, row(1) compact note("")) xlabel(none) xtitle("")
graph export "$dirpath/figures/eprice_lfit1_time.pdf", as(pdf) replace
twoway (scatter error1 day) if year > 2004, ///
	by(ym_name, row(1) compact note("")) xlabel(none) xtitle("")
graph export "$dirpath/figures/eprice_error1_time.pdf", as(pdf) replace
twoway (scatter eprice day) (line lfit1 day) if year > 2004, by(ym)
graph export "$dirpath/figures/eprice_lfit1.pdf", as(pdf) replace

qui reg eprice _Iyb_* _IybXind*
predict lfit2
twoway (scatter eprice indyb) (line lfit2 indyb) if year > 2004, ///
	by(yb_name, row(1) compact note("")) xlabel(none) xtitle("")
graph export "$dirpath/figures/eprice_lfit2_time.pdf", as(pdf) replace
twoway (scatter eprice indyb) (line lfit2 indyb) if year > 2004, by(yb)
graph export "$dirpath/figures/eprice_lfit2.pdf", as(pdf) replace

qui reg eprice _Iyq_* _IyqXind*
predict lfit3
twoway (scatter eprice indyq) (line lfit3 indyq) if year > 2004, ///
	by(yq_name, row(1) compact note("")) xlabel(none) xtitle("")
graph export "$dirpath/figures/eprice_lfit3_time.pdf", as(pdf) replace
twoway (scatter eprice indyq) (line lfit3 indyq) if year > 2004, by(yq)
graph export "$dirpath/figures/eprice_lfit3.pdf", as(pdf) replace


* ROBUSTNESS REGRESSIONS -------------------------------------------------------
use "$dirpath/stata_data/data_regressions_passthrough.dta", clear

drop time
egen time = group(year month day)

xi i.month*i.year i.weekd i.hour i.month|temp i.month|tempx i.ym|windx i.month*i.hour i.ym*i.hour i.month|day ///
	i.peak i.peak|eprice i.peak|leprice i.ym|time i.yb|time i.yq|time

// specification
global demandcontrols = "temp tempx humid"
global supplycontrols = "windx windx2"
global controls = "coal gas brent"
global basefe = "_Ihour_* _Iyear* _Iweek* _Imonth_*"
global controls1 = "hour#(c.coal c.gas c.brent) coal gas brent"

global maincost = "ecost2_peak ecost2_off"
global instruments = "eprice _IpeaXepric_1"

// robustness with linear time trends - NO Royal decree
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _ImonXhou* _ImonXtem* if rd == 0, robust
estimates store spec1

ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _IymXt* _ImonXhou* _ImonXtem* if rd == 0, robust
estimates store spec2

ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _IybXt* _ImonXhou* _ImonXtem* if rd == 0, robust
estimates store spec3

ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _IyqXt* _ImonXhou* _ImonXtem* if rd == 0, robust
estimates store spec4

// WRITE TABLE --------
local N_spec = 4
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_trends.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Cost Pass-through Regression with Trends} \label{tab:cost_pt_trends}" _n _n ///
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
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost2_peak]) ""
}
file write myfile " \\ " _n 
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost2_peak]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Mg. Emissions Costs - Off Peak "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost2_off]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost2_off]) ")"
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"Month-SampleXTime 		& N & Y & N & N \\" _n ///	
"Bimonth-SampleXTime	& N & N & Y & N \\" _n ///	
"Quarter-SampleXTime	& N & N & N & Y  \\[\sep]" _n 
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"Only peak hours are included (between 8am and 8pm). " _n ///
"All specifications include month of sample, weekday, and hour-month fixed effects, as well as weather and demand controls " _n ///
"(temperature-month, maximum temperature-month, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil interacted with hourly fixed effects). The marginal emissions cost is instrumented with the emissions price. " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile


// robustness with linear time trends - Royal decree
ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _ImonXhou* _ImonXtem*, robust
estimates store spec1_rd

ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _IymXt* _ImonXhou* _ImonXtem*, robust
estimates store spec2_rd

ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _IybXt* _ImonXhou* _ImonXtem*, robust
estimates store spec3_rd

ivregress 2sls mg_price ($maincost = $instruments) $supplycontrols $demandcontrols ///
						$controls1 $basefe _Iym_* _IyqXt* _ImonXhou* _ImonXtem*, robust
estimates store spec4_rd

// WRITE TABLE --------
local N_spec = 4
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_cost_pt_trends_rd.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Cost Pass-through Regression with Trends including Royal Decree Period} \label{tab:cost_pt_trends_rd}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
" \hline\hline " _n
forvalues i = 1(1)`N_spec' {
	file write myfile " & \textbf{(`i')} "
}
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n
	
file write myfile "Mg. Emissions Costs - Peak "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'_rd
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost2_peak]) ""
}
file write myfile " \\ " _n 
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'_rd
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost2_peak]) ")"
}
file write myfile " \\[\sep] " _n
file write myfile "Mg. Emissions Costs - Off Peak "
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'_rd
	file write myfile " &" 
	file write myfile " " %4.3f (_b[ecost2_off]) ""
}
file write myfile " \\ " _n
forvalues i = 1(1)`N_spec' {
	estimates restore spec`i'_rd
	file write myfile " &" 
	file write myfile " (" %4.3f (_se[ecost2_off]) ")"
}
file write myfile " \\[\sep]\hline\\[-\sep]" _n
file write myfile "" ///	
"Month-SampleXTime 		& N & Y & N & N \\" _n ///	
"Bimonth-SampleXTime	& N & N & Y & N \\" _n ///	
"Quarter-SampleXTime	& N & N & N & Y  \\[\sep]" _n
file write myfile "\hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to June 2007, includes all thermal units in the Spanish electricity market. " _n ///
"Only peak hours are included (between 8am and 8pm). " _n ///
"All specifications include month of sample, weekday, and hour-month fixed effects, as well as weather and demand controls " _n ///
"(temperature-month, maximum temperature-month, humidity), " _n ///
" supply controls (wind speed and wind speed squared); and common controls (commodity prices of " _n ///
"coal, gas, and oil interacted with hourly fixed effects). The marginal emissions cost is instrumented with the emissions price. " _n ///
"Robust standard errors in parentheses. Number of observations: $" %7.0fc (e(N)) "$.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile
