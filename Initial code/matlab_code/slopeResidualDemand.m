function [slope, qfirm] = slopeResidualDemand(bw, hour, qbid, pbid, direction, firm, priceS, priceD)

Nfirms = 4;
Nhours = max(hour);
slope = zeros(Nhours, Nfirms);
qfirm = zeros(Nhours, Nfirms);


for h = min(hour):max(hour)
       select = (hour==h);
       temp = find(select);
       for i = 1:4
          % datatt: quantity, price, firm
          datatt = sortrows(sortrows([qbid(temp,1).*direction(temp,1),pbid(temp,1),firm(temp,1)],1),2); 
          % adding demand up
          datatt = [datatt,datatt(:,1).*(datatt(:,3)~=i).*(datatt(:,1)>0), ...
                        datatt(:,1).*(datatt(:,1)<0)];
          [perr,pindex] = min(abs(datatt(:,2)-priceS(h))); 
          slopeS = sum(datatt(:,4).* ...
              pdf('normal',(repmat(priceS(h),size(datatt(:,2),1),1)-datatt(:,2))/bw,0,1),1)/bw;
          slopeD = -sum(datatt(:,5).* ...
              pdf('normal',(repmat(priceD(h),size(datatt(:,2),1),1)-datatt(:,2))/bw,0,1),1)/bw;
          slope(h,i) = slopeD + slopeS;
          qfirm(h,i) = sum(datatt(1:pindex,1).*(datatt(1:pindex,3)==i));
       end
end

end