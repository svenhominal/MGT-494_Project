clc;
clear all;
close all;

addpath('/Applications/ILOG/CPLEX_Studio_Academic/cplex/examples/src/matlab');
addpath('/Applications/ILOG/CPLEX_Studio_Academic/cplex/matlab/');
setenv('ILOG_LICENSE_FILE','/Applications/ILOG/access.ilm')

datapath = '/Users/macmreguant/Dropbox/DATA';
dirpath = '/Users/macmreguant/Dropbox/PROJECTS/internalization2';

%%
Nmodels = 3;
Nhour   = 24;
Nfirms  = 4;
bw    = 3;

% startup
solution = [];
solutionPrices = [];

for y = 2004:2006
if (y == 2006)
    M = 2;
else
    M = 12;
end
for m = 1:M
for d = 1:31

%------------------------load data--------------------------------
date =  y*10000 + m*100 + d;
ym = y*100 + m;
file = sprintf('%s/matlab_data/data_%d.csv',dirpath,date);

if (exist(file,'file'))
    
fprintf('Computing for date: %d %d %d \n', y, m, d);

data = importdata(file,',',1);
%--------------------clean data-----------------------------

rejected  = data.data(:,12);
data.data = data.data(rejected==0,:);
data.data = sortrows(data.data,7);
data.data = sortrows(data.data,4);

year = data.data(:,1);
month= data.data(:,2);
day  = data.data(:,3);
hour = data.data(:,4);
firm = data.data(:,5);
id   = data.data(:,6);
pbid = data.data(:,7);
qbid = data.data(:,8);
erate = data.data(:,9);
direction = data.data(:,10);
cost = data.data(:,13);

direction(direction==1) = -1;
direction(direction==2) = 1;

%------------- modify emissions rate to account for hydro ----------
erate_original = erate;
for h=1:24
    temp2 = find((hour==h).*(erate==0)); 
    for i = 1:length(temp2) 
       index = temp2(i);
       if (index > 1) 
            erate(index) = erate(index-1);
       end
    end
end
erate(direction == - 1) = 0;

%-------------- computing different passthroughs -------------------

Nbid    = length(pbid);
pbid    = repmat(pbid,1,Nmodels);

price    = zeros(Nhour,Nmodels);
pricealt = zeros(Nhour,Nmodels);
demand   = zeros(Nhour,Nmodels);
eratem   = zeros(Nhour,Nmodels);
slope1   = zeros(Nhour,Nmodels);
slope2   = zeros(Nhour,Nmodels);
slope3   = zeros(Nhour,Nmodels);
slope4   = zeros(Nhour,Nmodels);
quantity1= zeros(Nhour,Nmodels);
quantity2= zeros(Nhour,Nmodels);
quantity3= zeros(Nhour,Nmodels);
quantity4= zeros(Nhour,Nmodels);
qsol     = zeros(Nbid ,Nmodels); 

for n = 1:Nmodels
    
    % modifications to optimal bids
    if (n == 2)
       pbid(:,n) = pbid(:,1) + erate; 
    end
   
    % clear market
    sol = marketClearing(qbid,pbid(:,n),direction,hour); 
    qsol(:,n)    = sol.x;
    pricealt(:,n)= sol.dual(1:Nhour,1);
    for h=1:24
        temp = find((hour==h).*(qsol(:,n) > 0.001).*(direction == 1));
        [price(h,n), index] = max(pbid(temp, n));
        demand(h,n) = sum(qsol(temp,n));
        if (n == 1)
            temp = erate(temp);
            eratem(h,1) = temp(index);
        end
    end 
    
    % compute slope and quantites
    if (n == 3)
        price(:,n) = price(:,n) + 1;
    end
    [slopeO qfirmO] =  slopeResidualDemand(bw(1), hour, qbid, pbid(:,n), direction, firm, price(:,n), price(:,n));
    if (length(bw) > 1)
        for b = 2:length(bw)
            slopeO = slopeO + slopeResidualDemand(bw(1), hour, qbid, pbid(:,n), direction, firm, price(:,n), price(:,n));
        end
        slopeO = slopeO/b;
    end  
    slope1(:,n) = slopeO(:,1);
    slope2(:,n) = slopeO(:,2);
    slope3(:,n) = slopeO(:,3);
    slope4(:,n) = slopeO(:,4);
    quantity1(:,n) = qfirmO(:,1);
    quantity2(:,n) = qfirmO(:,2);
    quantity3(:,n) = qfirmO(:,3);
    quantity4(:,n) = qfirmO(:,4);    
    
end

% STORE RESULTS
solution = [solution; year, month, day, hour, qbid, pbid, qsol, erate, erate_original, direction];
for h = 1:Nhour
   solutionPrices = [solutionPrices; y, m, d, h, price(h,:), pricealt(h,:), demand(h,:), eratem(h), ...
                      slope1(h,:), quantity1(h,:), slope2(h,:), quantity2(h,:), ...
                      slope3(h,:), quantity3(h,:), slope4(h,:), quantity4(h,:)];
end

end

end
end
end

%% Export data to analyze with state
csvwrite('../matlab_data/passthrough_results.csv',solutionPrices);
save('../matlab_data/passthrough_results.mat');

%% GRAPHS

draws = random('unif',0,1, 1000, 1);

for f = 1:4
    
thish = 18;

close all

fig = figure(1);

ct = 1;

for y = 2004:2006
if (y == 2006)
    M = 2;
else
    M = 12;
end
for m = 1:M
for d = 1:31

%------------------------load data--------------------------------
date =  y*10000 + m*100 + d;
ym = y*100 + m;
file = sprintf('%s/matlab_data/data_%d.csv',dirpath,date);

if (exist(file,'file') && draws(ct) < 0.025)
    
fprintf('Computing for date: %d %d %d \n', y, m, d);

data = importdata(file,',',1);

%--------------------clean data-----------------------------
rejected  = data.data(:,12);
data.data = data.data(rejected==0,:);
data.data = sortrows(data.data,7);
data.data = sortrows(data.data,4);

year = data.data(:,1);
month= data.data(:,2);
day  = data.data(:,3);
hour = data.data(:,4);
firm = data.data(:,5);
id   = data.data(:,6);
pbid = data.data(:,7);
qbid = data.data(:,8);
erate = data.data(:,9);
direction = data.data(:,10);
cost = data.data(:,13);

direction(direction==1) = -1;
direction(direction==2) = 1;

erate_original = erate;
for h=1:24
    temp2 = find((hour==h).*(erate==0)); 
    for i = 1:length(temp2) 
       index = temp2(i);
       if (index > 1) 
            erate(index) = erate(index-1);
       end
    end
end
erate(direction == - 1) = 0;
    
Nbid      = length(pbid);
pbid      = repmat(pbid,1,2);
pbid(:,2) = pbid(:,1) + erate; 

% make graphs
datatt =  getResidualDemand(hour, qbid, pbid(:,1), direction, firm, f, thish);
datatt2 =  getResidualDemand(hour, qbid, pbid(:,2), direction, firm, f, thish);

figure(1);
hold on;
select = (datatt(:,6)<20000).*(datatt(:,6)>-30000);
stairs(datatt(select==1,6)/1000,datatt(select==1,2))
hold off;

if (y == 2005)
fig2 = figure(2);
sol = marketClearing(qbid,pbid(:,1),direction,hour);
qsol = sol.x;
for h=1:24
    temp = find((hour==h).*(qsol > 0.001).*(direction == 1));
    [price(h), index] = max(pbid(temp,1));
end
plow = price(thish) - 15;
phigh = price(thish) + 15;
hold on;
select = (datatt(:,2)>plow).*(datatt(:,2)<phigh);
stairs(datatt(select==1,6)/1000,datatt(select==1,2))
stairs(datatt(select==1,7)/1000,datatt(select==1,2))
select = (datatt2(:,2)>plow).*(datatt2(:,2)<phigh);
stairs(datatt2(select==1,6)/1000,datatt2(select==1,2))
stairs(datatt2(select==1,7)/1000,datatt2(select==1,2))
hold off;
xlabel('GWh')
ylabel('Euro/MWh')
file = sprintf('../figures/residual_shift_%d_%d.png',f,thish);
print(fig2, '-dpng', file)
close 2
end

end

ct = ct + 1;

end
end
end

xlabel('GWh')
ylabel('Euro/MWh')
%title(sprintf('Firm %d Sample Residual Demands',f))
file = sprintf('../figures/residual%d_%d.png',f,thish);
print(fig, '-dpng', file)

end
