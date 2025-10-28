* DATA SUMMARY GRAPHS

// CO2 prices during the EU-ETS Trial Period
use "$dirpath/stata_data/data_regressions_passthrough.dta", clear
keep year month day eprice mg_price
duplicates drop
drop if year < 2004 | year > 2007 | (year == 2007 & month > 6)

collapse (mean) eprice mg_price (max) max_price=mg_price (min) min_price=mg_price, by(year month day)

gen time = mdy(month,day,year)
format time %d

// REDUCED SAMPLE
twoway (tsline eprice) (tsline mg_price) if year < 2006 | (year == 2006 & month < 3), graphregion(color(white)) ///
tlabel( 01jan2004 "2004" 01jan2005 "2005" 01jan2006 "2006") ///
legend(order(2 "Daily Electricity Price (E/MWh)" 1 "Emissions Price (E/ton)")) ///
scheme(sj) ytitle("Euros") xtitle("") 
*title("Spanish Electricity Prices and CO{subscript:2} Prices")
graph export "$dirpath/figures/prices_sample_reduced.eps", as(eps) replace
graph export "$dirpath/figures/prices_sample_reduced.pdf", as(pdf) replace


// marginal emissions rate
use "$dirpath/stata_data/data_regressions_passthrough.dta", clear	

// generate measures of emissions cost and marginal cost
keep year month day hour erate
duplicates drop

drop if year > 2006
drop if year == 2006 & month > 2

twoway lpolyci erate hour, scheme(sj) graphregion(color(white)) ///
	ytitle("Emissions Rate (Tons CO{subscript:2}/MWh)") xtitle("Hour of the Day") ///
	xlabel(1(1)24) legend(order(2 "Emissions Rate" 1 "CI 95%"))
graph export "$dirpath/figures/erate_hour.eps", as(eps) replace
graph export "$dirpath/figures/erate_hour.pdf", as(pdf) replace	
