* DATA SUMMARY

// Bidding Data Analysis
use "$dirpath/stata_data/data_regressions_lite.dta", clear

sort up year month day hour price
by up year month day hour: gen step = _n
by up year month day hour: gen numstep = _N
gen medmwh = (mw-minmw)/2 + minmw
by up year month day hour: gen medprice = price if cummwh >= medmwh & cummwh[_n-1] < medmwh
by up year month day hour: replace medprice = price if cummwh >= medmwh & step == 1 & bilateral == 0

collapse (mean) price medprice accepted rejected bilateral erate cost_CO2 eprice numstep, by(year month day hour up weekd firm firm_code fuel)

// rounding to compare prcies
replace price = round(price,.01)
replace medprice = round(medprice,.01)

// comparison for the same hour in consecutive days
egen id = group(up hour firm)
gen time = mdy(month,day,year)
format time %d

isid id time
tsset id time

gen adj1 = .
replace adj1 = 0 if price == L.price & L.price != .
replace adj1 = 1 if price != L.price & L.price != .

gen adj2 = .
replace adj2 = 0 if medprice == L.medprice & L.medprice != .
replace adj2 = 1 if medprice != L.medprice & L.medprice != .

summ adj1 adj2

sort id weekd year month day
by id weekd: gen weekid = _n

egen id2 = group(up hour firm weekd)

isid id2 weekid
tsset id2 weekid

gen adj3 = .
replace adj3 = 0 if price == L.price & L.price != .
replace adj3 = 1 if price != L.price & L.price != .

gen adj4 = .
replace adj4 = 0 if medprice == L.medprice & L.medprice != .
replace adj4 = 1 if medprice != L.medprice & L.medprice != .

summ adj3 adj4

sort hour year month day firm
by hour year month day firm: egen adj5 = max(adj1) if adj1 != .
by hour year month day firm: egen adj6 = max(adj2) if adj2 != .
by hour year month day firm: replace adj5 = . if _n != 1
by hour year month day firm: replace adj6 = . if _n != 1

summ adj5 adj6

tabstat adj*, by(weekd)
tabstat adj*, by(firm)

// generate table of adjustments
local N_spec = 3
local weeknames = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday"
capture file close myfile
file open myfile using "$dirpath/tables/tab_frequency.tex", write replace
file write myfile "\begin{table}" _n ///
"\centering" _n ///
"\caption{Frequency of Bid Changes}\label{tab:frequency}" _n ///
"\begin{tabular*}{0.8\textwidth}{@{\extracolsep{\fill}} l" 
forvalues i = 1(1)`N_spec' {
	file write myfile "r"
}
file write myfile "}" _n ///
" \hline\hline \\[-\sep] " _n
file write myfile " & \multicolumn{1}{c}{{Previous Day}} " ///
" & \multicolumn{1}{c}{{Previous Week}} " ///
" & \multicolumn{1}{c}{{Previous Day}} \\ " _n
file write myfile " & \multicolumn{1}{c}{{Unit-Level}} " ///
" & \multicolumn{1}{c}{{Unit-Level}} " ///
" & \multicolumn{1}{c}{{Firm-Level}} " _n
file write myfile  "\\ \cline{2-2} \cline{3-3} \cline{4-4} \\[-\sep] " _n
// mg price
file write myfile "All days "
forvalues i = 1(1)`N_spec' {
	local j = 1 + (`i'-1)*2
	qui summ adj`j'
	file write myfile " & " %4.3f (`r(mean)')
}
file write myfile  "  \\[\sep] "
forvalues w = 1(1)7 {
local wname = word("`weeknames'",`w')
file write myfile _n " `wname' "
forvalues i = 1(1)`N_spec' {
	local j = 1 + (`i'-1)*2
	qui summ adj`j' if weekd == `w'
	file write myfile " & " %4.3f (`r(mean)')
}
file write myfile  "\\"
}
file write myfile " \hline\hline " _n ///
"\end{tabular*}" _n ///
"\begin{minipage}[c]{0.8\textwidth}" _n ///
"{\footnotesize " _n ///
"\noindent" _n ///
"Notes: Table reports the average frequency of times in which the average or median price bid of a given " _n ///
"unit changes. The average bid is defined as the average of prices across the supply function " _n ///
"of a unit. Columns 1 compares the bids with the same hour of the previous day. " _n ///
"Columns 2 compares the bids with the same hour and weekday of the previous week. " _n ///
"Columns 3 reports whether any changes occured at the firm level. " _n ///
"}" _n ///
"\end{minipage}"  _n ///
"\end{table}" _n
file close myfile
