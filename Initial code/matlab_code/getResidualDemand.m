function datatt = getResidualDemand(hour, qbid, pbid, direction, firm, f, h)

temp = find((hour==h));

% datatt: quantity, price, firm
datatt = sortrows(sortrows([qbid(temp,1).*direction(temp,1),pbid(temp,1),firm(temp,1)],1),2);
% adding demand up
datatt = [datatt,repmat(-sum(datatt(:,1).*(datatt(:,1)<0)),length(datatt),3),zeros(length(datatt),1)];
for j = 2:length(datatt)
    % supply only
    datatt(j,4) = datatt(j-1,4) - abs(datatt(j-1,1)).*(datatt(j-1,3)~=f).*(datatt(j-1,1)>0);
    % demand only
    datatt(j,5) = datatt(j-1,5) - abs(datatt(j-1,1)).*(datatt(j-1,1)<0);
    % supply and demand
    datatt(j,6) = datatt(j-1,6) - abs(datatt(j-1,1)).*(datatt(j-1,3)~=f).*(datatt(j-1,1)>0) ...
                                - abs(datatt(j-1,1)).*(datatt(j-1,1)<0);
	% my supply
    datatt(j,7) = datatt(j-1,7) + abs(datatt(j-1,1)).*(datatt(j-1,3)==f).*(datatt(j-1,1)>0);
end

end
