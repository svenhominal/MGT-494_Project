*** MARKUP ANALYSIS ***

clear
set matsize 2000
log close _all

insheet using "$dirpath/matlab_data/passthrough_results.csv", clear comma
rename v1 year
rename v2 month
rename v3 day
rename v4 hour
rename v5 price0
rename v6 price1
rename v7 price2
rename v8 pricea0
rename v9 pricea1
rename v10 pricea2
rename v11 demand0
rename v12 demand1
rename v13 demand2
rename v14 eratem
rename v15 slope1_0
rename v16 slope1_1
rename v17 slope1_2
rename v18 qfirm1_0
rename v19 qfirm1_1
rename v20 qfirm1_2
rename v21 slope2_0
rename v22 slope2_1
rename v23 slope2_2
rename v24 qfirm2_0
rename v25 qfirm2_1
rename v26 qfirm2_2
rename v27 slope3_0
rename v28 slope3_1
rename v29 slope3_2
rename v30 qfirm3_0
rename v31 qfirm3_1
rename v32 qfirm3_2
rename v33 slope4_0
rename v34 slope4_1
rename v35 slope4_2
rename v36 qfirm4_0
rename v37 qfirm4_1
rename v38 qfirm4_2

save "$dirpath/stata_data/passthrough_results.dta", replace

forvalues s = 0(1)2 {
	gen lprice`s' = log(price`s')
}

forvalues f = 1(1)4 {
forvalues s = 0(1)2 {
	gen elas`f'_`s'   = slope`f'_`s'*price`s'/qfirm`f'_`s'
	gen lelas`f'_`s'  = log(elas`f'_`s')
	gen markup`f'_`s' = qfirm`f'_`s'/slope`f'_`s'
	gen lmarkup`f'_`s'= log(markup`f'_`s')
	gen lslope`f'_`s' = log(1/slope`f'_`s') 
	gen lqfirm`f'_`s' = log(qfirm`f'_`s') 
}
}

forvalues f = 1(1)4 {
	gen superelas`f' = ((elas`f'_1-elas`f'_0)/elas`f'_0)/((price1-price0)/price0)
	gen superelas_fix`f' = ((elas`f'_2-elas`f'_0)/elas`f'_0)/((price2-price0)/price0)
	gen chqfirm`f' = ((qfirm`f'_1-qfirm`f'_0)/qfirm`f'_0)*100
	gen chslope`f' = ((slope`f'_1-slope`f'_0)/slope`f'_0)*100
	gen chmarkup`f'= ((markup`f'_1-markup`f'_0)/markup`f'_0)*100
	gen deltaqfirm`f' = ((qfirm`f'_1-qfirm`f'_0))
	gen deltaslope`f' = ((slope`f'_1-slope`f'_0))
	gen deltamarkup`f'= ((markup`f'_1-markup`f'_0))
}
gen chdemand = ((demand1-demand0)/demand0)*100


// co2 prices
sort year month day
merge year month day using "$dirpath/stata_data/data_eua_prices.dta", nokeep keep(eprice)
drop _merge
replace eprice = 0 if year == 2004
gen leprice = log(eprice + 1)



// table summary of elasticities ***********************************************
local N_spec = 5
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_elas.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Elaticity Summary Statistics} \label{tab:elas}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
file write myfile " & \textbf{Obs}  & \textbf{Mean}  & \textbf{SD}  & \textbf{Min}  & \textbf{Max} "
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n

forvalues f = 1(1)4 {
qui summ elas`f'_0, det
local lower = `r(p1)'
local upper = `r(p99)'
summ elas`f'_0 if elas`f'_0 > `lower' & elas`f'_0 < `upper'
					
file write myfile "Firm `f' $(\eta_`f')$ "
file write myfile " &" 
file write myfile " " %6.0fc (`r(N)') ""
file write myfile " &" 
file write myfile " " %4.1f (`r(mean)') ""
file write myfile " &" 
file write myfile " " %4.1f (`r(sd)') ""
file write myfile " &" 
file write myfile " " %4.1f (`r(min)') ""
file write myfile " &" 
file write myfile " " %4.1f (`r(max)') ""

file write myfile " \\[\sep] " _n
}
// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline \vspace{-18pt}" _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize \vspace{6pt}" _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
" Slope of residual demand estimated using a Gaussian Kernel with bandwidth set to 3\euro.}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile


// table summary of elasticities ***********************************************
local N_spec = 5
local N_spec1 = `N_spec'+1
local N_spec_1 = `N_spec'-1
capture file close myfile
file open myfile using "$dirpath/tables/table_qfirm.tex", write replace	
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Percent Changes in Quantities, Markups and Slopes} \label{tab:qfirm}" _n _n ///
"\begin{tabular*}{.9\textwidth}{@{\extracolsep{\fill}} l " 
forvalues i = 1(1)`N_spec' {
	file write myfile " c "
}
file write myfile "}" _n ///
"\hline\hline " _n
file write myfile " & \textbf{Mean}  & \textbf{SD}  & \textbf{P25}  & \textbf{P50} & \textbf{P75}  "
file write myfile  "\\ \cline{2-`N_spec1'} \\[-\sep]" _n

file write myfile "\textbf{Changes in Quantity }  \\[\sep]" _n
summ chdemand, det
file write myfile "\quad Aggregate Demand "
file write myfile " &"
file write myfile " " %4.1f (`r(mean)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(sd)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p25)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p50)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p75)') "\%"

file write myfile " \\[\sep] " _n

forvalues f = 1(1)4 {

summ chqfirm`f', det
					
file write myfile "\quad Firm `f' "
file write myfile " &"
file write myfile " " %4.1f (`r(mean)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(sd)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p25)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p50)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p75)') "\%"

file write myfile " \\[\sep] " _n
}

file write myfile "\hline \\[-\sep]" _n

file write myfile "\textbf{Changes in Slope} \\ \textbf{of Inverse Residual Demand} \\[\sep]" _n
forvalues f = 1(1)4 {

summ chslope`f',det
					
file write myfile "\quad Firm `f' "
file write myfile " &"
file write myfile " " %4.1f (`r(mean)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(sd)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p25)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p50)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p75)') "\%"

file write myfile " \\[\sep] " _n
}

file write myfile "\hline \\[-\sep]" _n

file write myfile "\textbf{Changes in Markup}  \\[\sep]" _n
forvalues f = 1(1)4 {

summ chmarkup`f', det
					
file write myfile "\quad Firm `f' "
file write myfile " &"
file write myfile " " %4.1f (`r(mean)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(sd)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p25)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p50)') "\%"
file write myfile " &" 
file write myfile " " %4.1f (`r(p75)') "\%"

file write myfile " \\[\sep] " _n
}

// revise specifications and description so that it reflects regressions
file write myfile "\hline\hline \vspace{-18pt}" _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{.9\textwidth}" _n ///
"{\footnotesize \vspace{6pt}" _n ///
"\noindent" _n ///
"Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. " _n ///
"Table expresses percent changes in quantities, markups and the slope of the inverse residual demand for a one euro " _n ///
"increase in carbon prices. Number of observations: 18,960. } \end{minipage}"  _n ///
"\end{table}" _n
file close myfile
